import moment from 'moment';
moment().utc(true);
moment.suppressDeprecationWarnings = true;

export type Timestamp = moment.Moment | string;
export type Mapping = { [k: string]: any } | string;
export type Collection = any[] | string;

export const parseTimestamp = (timestamp: string) =>
  moment.utc(timestamp);
export interface AttributeDefintion {
  type:
    | 'string'
    | 'integer'
    | 'float'
    | 'enum'
    | 'timestamp'
    | 'epoch'
    | 'mapping'
    | 'collection'
    | 'blob';
  required?: boolean;
  description?: string;
  enum_def?: string[];
  business_id?: boolean;
}

type EntityAttributes = { [k: string]: AttributeDefintion };

type EntitySchemaExtension = { [k: string]: any };

export type EntitySchema = {
  name: string;
  namespace: string;
  metatype: 'noun' | 'relationship';
  extensions?: EntitySchemaExtension;
  attributes: EntityAttributes;
};

export interface NounSchema extends EntitySchema {
  metatype: 'noun';
}
export interface RelationshipSchema extends EntitySchema {
  metatype: 'relationship';
  ref_from: string;
  ref_to: string;
}

type AttributeType<A extends AttributeDefintion> = A['type'] extends
  | 'string'
  | 'blob'
  ? string
  : A['type'] extends 'integer' | 'float' | 'epoch'
  ? number
  : A['type'] extends 'mapping'
  ? Mapping
  : A['type'] extends 'collection'
  ? Collection
  : A['type'] extends 'timestamp'
  ? Timestamp
  : any;

type RequiredAttributeKeys<D extends EntitySchema> = {
  [P in keyof D['attributes']]: D['attributes'][P]['required'] extends true
    ? P
    : never;
}[keyof D['attributes']];

type NonRequiredAttributeKeys<D extends EntitySchema> = {
  [P in keyof D['attributes']]: D['attributes'][P]['required'] extends true
    ? never
    : P;
}[keyof D['attributes']];

type EntityType<D extends EntitySchema> = {
  identifier?: string | undefined;
  __schema?: string | undefined;
} & {
  [Property in RequiredAttributeKeys<D>]: AttributeType<
    D['attributes'][Property]
  >;
} & {
  [Property in NonRequiredAttributeKeys<D>]?: AttributeType<
    D['attributes'][Property]
  >;
};

export type EntityData<D extends Entity> = EntityType<
  ReturnType<D['entityDefinition']>
>;

const validateAttributeValue = (
  attr: string,
  attribute: AttributeDefintion,
  value: any,
) => {
  const typemap = {
    string: ['string'],
    integer: ['number'],
    float: ['number'],
    enum: ['string'],
    mapping: ['object', 'string'],
    collection: ['object', 'string'],
    blob: ['string'],
    timestamp: ['object', 'string'],
    epoch: ['number'],
  };

  if (value === undefined && attribute.required) {
    throw new Error(`Required field, ${attr}, cannot be undefined`);
  } else if (value === undefined && attribute.required !== true) {
    return value;
  }
  if (typemap[attribute.type].indexOf(typeof value) <= -1) {
    throw new Error(
      `Invalid type for "${attr}", must be ${attribute.type}`,
    );
  }

  const decodeJSONBlob = (value: string) => {
    try {
      return JSON.parse(value);
    } catch (error) {
      return JSON.parse(atob(value));
    }
  };

  if (attribute.type === 'collection') {
    if (typeof value === 'string') value = decodeJSONBlob(value);
    if (!Array.isArray(value))
      throw new Error(`Field, ${attr}, must be an array`);
  }
  if (attribute.type === 'mapping') {
    if (typeof value === 'string') value = decodeJSONBlob(value);
    if (typeof value !== 'object' || Array.isArray(value))
      throw new Error(`Field, ${attr}, must be an object`);
  }
  if (
    attribute.type === 'enum' &&
    attribute.enum_def?.indexOf(value) === -1
  ) {
    throw new Error(
      `Field, ${attr}, must be one of ${attribute.enum_def.join(
        ', ',
      )}`,
    );
  }
  if (attribute.type === 'timestamp') {
    if (!moment(value).isValid())
      throw new Error(`Invalid date format for ${attr}`);
    return parseTimestamp(value).toISOString();
  }

  return value;
};

export type SerializationOptions = {
  encodeBlobs?: boolean;
  includeSchema?: boolean;
};
export abstract class Entity {
  _identifier: string | undefined;
  constructor(obj: EntityData<Entity>) {
    this._identifier = obj.identifier;
  }

  abstract entityDefinition(): EntitySchema;
  protected abstract data: EntityData<Entity>;

  protected _setter(attr: string, value: any) {
    return validateAttributeValue(
      attr,
      this.entityDefinition().attributes[attr],
      value,
    );
  }

  public get identifier(): string | undefined {
    return this._identifier;
  }

  public set identifier(v: string | undefined) {
    this._identifier = v;
  }

  public get namespaceName(): string {
    const entity_definition = this.entityDefinition();
    let name = entity_definition.name;
    let namespace = entity_definition.namespace;
    return `${namespace !== undefined ? namespace + '.' : ''}${name}`;
  }

  protected _serialize(
    { encodeBlobs, includeSchema }: SerializationOptions = {
      encodeBlobs: true,
      includeSchema: false,
    },
  ): EntityData<Entity> {
    const entity_definition = this.entityDefinition();
    let result: any = {};

    if (this.identifier) result.identifier = this.identifier;

    for (let attr in entity_definition.attributes) {
      let attrDef = entity_definition.attributes[attr];
      let value: any = this.data[attr as keyof EntityData<Entity>];

      if (value != null) {
        if (['collection', 'mapping'].indexOf(attrDef.type) > -1) {
          if (encodeBlobs) value = btoa(JSON.stringify(value));
        } else if (attrDef.type === 'blob') {
          value = btoa(value);
        }
        result[attr as keyof EntityData<Entity>] = value;
      }
    }

    if (includeSchema) result['__schema'] = this.namespaceName;

    return result as EntityData<Entity>;
  }

  public setEquals(other: Entity) {
    if (other.namespaceName === this.namespaceName) {
      for (const attr in this.entityDefinition().attributes) {
        this.data[attr] = this._setter(attr, other.data[attr]);
      }
    }
  }

  static deserialize(
    schema: EntitySchema,
    data: EntityType<EntitySchema>,
  ) {
    const newData = { ...data };
    if (newData['__schema']) {
      if (
        `${
          schema.namespace !== undefined ? schema.namespace + '.' : ''
        }${schema.name}` !== newData['__schema']
      )
        throw new Error('Mismatching schemas in deserialize call');
      delete newData['__schema'];
    }
    for (let attr in schema.attributes) {
      if (newData[attr]) {
        let result = newData[attr];
        if (schema.attributes[attr].type === 'timestamp') {
          result = parseTimestamp(result);
        } else if (
          ['mapping', 'collection'].indexOf(
            schema.attributes[attr].type,
          ) >= 0
        ) {
          result = JSON.parse(atob(result));
        } else if (schema.attributes[attr].type === 'blob') {
          result = atob(result);
        }
        newData[attr] = result;
      }
    }

    return schema.metatype === 'noun'
      ? nounFactory(schema as NounSchema, newData)
      : relationshipFactory(
          schema as RelationshipSchema,
          newData,
          newData['ref_from'],
          newData['ref_to'],
        );
  }
}

export abstract class Noun extends Entity {
  to_rels: { [k: string]: Relationship<Noun, Noun>[] } = {};
  from_rels: { [k: string]: Relationship<Noun, Noun>[] } = {};

  abstract entityDefinition(): NounSchema;

  public serialize(opts?: SerializationOptions): EntityData<Noun> {
    return this._serialize(opts);
  }
}

export abstract class Relationship<
  TFrom extends string | Noun = string,
  TTo extends string | Noun = string,
> extends Entity {
  private _ref_from?: TFrom;
  private _ref_to?: TTo;

  constructor(
    obj: EntityData<Relationship<TFrom, TTo>>,
    ref_from?: TFrom,
    ref_to?: TTo,
  ) {
    super(obj);
    this._ref_from = ref_from;
    this._ref_to = ref_to;
  }

  abstract entityDefinition(): RelationshipSchema;

  public serialize(
    opts?: SerializationOptions,
  ): EntityData<Relationship> {
    const result = this._serialize(opts);
    if (this.refFrom !== undefined) {
      result.ref_from = this.refFrom;
    }
    if (this.refTo !== undefined) {
      result.ref_to = this.refTo;
    }

    return result;
  }

  public get refFrom(): TFrom | undefined {
    return this._ref_from;
  }

  public set refFrom(v: TFrom | undefined) {
    this._ref_from = v;
  }

  public get refTo(): TTo | undefined {
    return this._ref_to;
  }

  public set refTo(v: TTo | undefined) {
    this._ref_to = v;
  }
}

export function nounFactory(
  definition: NounSchema,
  obj: EntityType<EntitySchema>,
) {
  const validateObj = (obj: EntityType<EntitySchema>) => {
    const attributes = new Set(Object.keys(definition.attributes));
    const requiredFields = new Set(
      Object.keys(definition.attributes).filter(
        (attr) => definition.attributes[attr].required === true,
      ),
    );
    const objFields = new Set(Object.keys(obj));

    const missingFields = [...Array.from(requiredFields)].filter(
      (v) => !objFields.has(v),
    );

    if (missingFields.length > 0)
      throw new Error(
        `Missing required fields: ${missingFields.join(', ')}`,
      );

    const extraFields = [...Array.from(objFields)].filter(
      (v) => !attributes.has(v) && v !== 'identifier',
    );

    if (extraFields.length > 0)
      throw new Error(
        `Extra fields found: ${extraFields.join(', ')}`,
      );
    let data: any = {};
    for (let attr of Array.from(attributes)) {
      let value = validateAttributeValue(
        attr,
        definition.attributes[attr],
        obj[attr as keyof EntityType<EntitySchema>],
      );
      data[attr] = value;
    }

    return data as EntityType<EntitySchema>;
  };

  class GenericNoun extends Noun {
    entityDefinition(): NounSchema {
      return definition;
    }
    protected data: EntityType<EntitySchema>;

    constructor(obj: EntityType<EntitySchema>) {
      super(obj);
      this.data = validateObj(obj);

      for (let attr in this.data) {
        Object.defineProperty(this, attr, {
          get: () =>
            this.data[attr as keyof EntityType<EntitySchema>],
          set: (value: any) => {
            this.data[attr as keyof EntityType<EntitySchema>] =
              this._setter(attr, value);
          },
        });
      }
    }
  }

  const noun: unknown = new GenericNoun(obj);
  return noun as Noun & EntityType<EntitySchema>;
}

export function relationshipFactory<
  TFrom extends string | Noun = string,
  TTo extends string | Noun = string,
>(
  definition: RelationshipSchema,
  obj: EntityType<EntitySchema>,
  refFrom?: TFrom,
  refTo?: TTo,
) {
  const validateObj = (obj: EntityType<EntitySchema>) => {
    const attributes = new Set(Object.keys(definition.attributes));
    const requiredFields = new Set(
      Object.keys(definition.attributes).filter(
        (attr) => definition.attributes[attr].required === true,
      ),
    );
    const objFields = new Set(Object.keys(obj));

    const missingFields = [...Array.from(requiredFields)].filter(
      (v) => !objFields.has(v),
    );

    if (missingFields.length > 0)
      throw new Error(
        `Missing required fields: ${missingFields.join(', ')}`,
      );

    const extraFields = [...Array.from(objFields)].filter(
      (v) =>
        !attributes.has(v) &&
        v !== 'identifier' &&
        v !== 'ref_from' &&
        v !== 'ref_to',
    );

    if (extraFields.length > 0)
      throw new Error(
        `Extra fields found: ${extraFields.join(', ')}`,
      );
    let data: any = {};
    for (let attr of Array.from(attributes)) {
      let value = validateAttributeValue(
        attr,
        definition.attributes[attr],
        obj[attr as keyof EntityType<EntitySchema>],
      );
      data[attr] = value;
    }

    return data as EntityType<EntitySchema>;
  };

  class GenericRelationship extends Relationship<TFrom, TTo> {
    entityDefinition(): RelationshipSchema {
      return definition;
    }
    protected data: EntityType<EntitySchema>;

    constructor(
      obj: EntityType<EntitySchema>,
      from?: TFrom,
      to?: TTo,
    ) {
      super(obj, from, to);
      this.data = validateObj(obj);

      for (let attr in this.data) {
        Object.defineProperty(this, attr, {
          get: () =>
            this.data[attr as keyof EntityType<EntitySchema>],
          set: (value: any) => {
            this.data[attr as keyof EntityType<EntitySchema>] =
              this._setter(attr, value);
          },
        });
      }
    }
  }

  const relationship: unknown = new GenericRelationship(
    obj,
    refFrom,
    refTo,
  );
  return relationship as Relationship<TFrom, TTo> &
    EntityType<EntitySchema>;
}
