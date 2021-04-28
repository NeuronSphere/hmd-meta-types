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
  metatype: 'noun' | 'relationshp';
  attributes: EntityAttributes;
};

type AttributeType<
  A extends AttributeDefintion
> = A['type'] extends 'string'
  ? string
  : A['type'] extends 'integer' | 'float'
  ? number
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

export type EntityInput<D extends Entity> = EntityType<
  ReturnType<D['entityDefinition']>
>;

export abstract class Entity {
  _identifier: string | undefined;
  constructor(obj: EntityInput<Entity>) {
    this._identifier = obj.identifier;
  }

  abstract entityDefinition(): EntityDefinition;
  protected abstract data: EntityInput<Entity>;

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

  public serialize(): EntityInput<Entity> {
    const entity_definition = this.entityDefinition();
    let result: any = {};

    if (this.identifier) result.identifier = this.identifier;

    for (let attr in entity_definition.attributes) {
      let attrDef = entity_definition.attributes[attr];
      let value: any = this.data[attr as keyof EntityInput<Entity>];

      if (value != null) {
        if (
          ['collection', 'mapping', 'blob'].indexOf(attrDef.type) > -1
        ) {
          value = btoa(JSON.stringify(value));
        }
        result[attr as keyof EntityInput<Entity>] = value;
      }
    }

    return result as EntityInput<Entity>;
  }
}

export abstract class Noun extends Entity {
  to_rels: { [k: string]: Relationship<Noun, Noun>[] } = {};
  from_rels: { [k: string]: Relationship<Noun, Noun>[] } = {};
}

export abstract class Relationship<TFrom, TTo> extends Entity {
  private _ref_from: TFrom;
  private _ref_to: TTo;

  constructor(
    obj: EntityInput<Relationship<TFrom, TTo>>,
    ref_from: TFrom,
    ref_to: TTo,
  ) {
    super(obj);
    this._ref_from = ref_from;
    this._ref_to = ref_to;
  }

  public get ref_from(): TFrom {
    return this._ref_from;
  }

  public set ref_from(v: TFrom) {
    this._ref_from = v;
  }

  public get ref_to(): TTo {
    return this._ref_to;
  }

  public set ref_to(v: TTo) {
    this._ref_to = v;
  }
}
