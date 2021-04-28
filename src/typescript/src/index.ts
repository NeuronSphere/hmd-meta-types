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
}

type EntityAttributes = { [k: string]: AttributeDefintion };

export type EntityDefinition = {
  name: string;
  namespace: string;
  metatype: 'noun' | 'relationship';
  attributes: EntityAttributes;
};

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

type RequiredAttributeKeys<D extends EntityDefinition> = {
  [P in keyof D['attributes']]: D['attributes'][P]['required'] extends true
    ? P
    : never;
}[keyof D['attributes']];

type NonRequiredAttributeKeys<D extends EntityDefinition> = {
  [P in keyof D['attributes']]: D['attributes'][P]['required'] extends true
    ? never
    : P;
}[keyof D['attributes']];

type EntityType<D extends EntityDefinition> = {
  identifier?: string | undefined;
} & {
  [Property in RequiredAttributeKeys<D>]: AttributeType<
    D['attributes'][Property]
  >;
} &
  {
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
  if (attribute.type === 'collection') {
    if (typeof value === 'string') value = atob(value);
    if (!Array.isArray(value))
      throw new Error(`Field, ${attr}, must be an array`);
  }
  if (attribute.type === 'mapping') {
    if (typeof value === 'string') value = atob(value);
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
export abstract class Entity {
  _identifier: string | undefined;
  constructor(obj: EntityData<Entity>) {
    this._identifier = obj.identifier;
  }

  abstract entityDefinition(): EntityDefinition;
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

  protected _serialize(): EntityData<Entity> {
    const entity_definition = this.entityDefinition();
    let result: any = {};

    if (this.identifier) result.identifier = this.identifier;

    for (let attr in entity_definition.attributes) {
      let attrDef = entity_definition.attributes[attr];
      let value: any = this.data[attr as keyof EntityData<Entity>];

      if (value != null) {
        if (
          ['collection', 'mapping', 'blob'].indexOf(attrDef.type) > -1
        ) {
          value = btoa(JSON.stringify(value));
        }
        result[attr as keyof EntityData<Entity>] = value;
      }
    }

    return result as EntityData<Entity>;
  }
}

export abstract class Noun extends Entity {
  to_rels: { [k: string]: Relationship<Noun, Noun>[] } = {};
  from_rels: { [k: string]: Relationship<Noun, Noun>[] } = {};

  public serialize(): EntityData<Noun> {
    return this._serialize();
  }
}

export abstract class Relationship<
  TFrom extends Noun = Noun,
  TTo extends Noun = Noun
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

  public serialize(): EntityData<Relationship> {
    const result = this._serialize();
    if (this.refFrom !== undefined) {
      result.ref_from = this.refFrom.serialize();
    }
    if (this.refTo !== undefined) {
      result.ref_to = this.refTo.serialize();
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
  definition: EntityDefinition,
  obj: EntityType<EntityDefinition>,
) {
  const validateObj = (obj: EntityType<EntityDefinition>) => {
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
      (v) => !attributes.has(v),
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
        obj[attr as keyof EntityType<EntityDefinition>],
      );
      data[attr] = value;
    }

    return data as EntityType<EntityDefinition>;
  };

  class GenericNoun extends Noun {
    entityDefinition(): EntityDefinition {
      return definition;
    }
    protected data: EntityType<EntityDefinition>;

    constructor(obj: EntityType<EntityDefinition>) {
      super(obj);
      this.data = validateObj(obj);

      for (let attr in this.data) {
        Object.defineProperty(this, attr, {
          get: () =>
            this.data[attr as keyof EntityType<EntityDefinition>],
          set: (value: any) => {
            this.data[
              attr as keyof EntityType<EntityDefinition>
            ] = this._setter(attr, value);
          },
        });
      }
    }
  }

  const noun: unknown = new GenericNoun(obj);
  return noun as Noun & EntityType<EntityDefinition>;
}

export function relationshipFactory<
  TFrom extends Noun = Noun,
  TTo extends Noun = Noun
>(
  definition: EntityDefinition,
  obj: EntityType<EntityDefinition>,
  refFrom?: TFrom,
  refTo?: TTo,
) {
  const validateObj = (obj: EntityType<EntityDefinition>) => {
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
      (v) => !attributes.has(v),
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
        obj[attr as keyof EntityType<EntityDefinition>],
      );
      data[attr] = value;
    }

    return data as EntityType<EntityDefinition>;
  };

  class GenericRelationship extends Relationship<TFrom, TTo> {
    entityDefinition(): EntityDefinition {
      return definition;
    }
    protected data: EntityType<EntityDefinition>;

    constructor(
      obj: EntityType<EntityDefinition>,
      from?: TFrom,
      to?: TTo,
    ) {
      super(obj, from, to);
      this.data = validateObj(obj);

      for (let attr in this.data) {
        Object.defineProperty(this, attr, {
          get: () =>
            this.data[attr as keyof EntityType<EntityDefinition>],
          set: (value: any) => {
            this.data[
              attr as keyof EntityType<EntityDefinition>
            ] = this._setter(attr, value);
          },
        });
      }
    }
  }

  const noun: unknown = new GenericRelationship(obj, refFrom, refTo);
  return noun as Noun & EntityType<EntityDefinition>;
}
