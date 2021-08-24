import {
  EntitySchema,
  EntityData,
  Noun,
  nounFactory,
  Timestamp,
  parseTimestamp,
  Mapping,
  Collection,
  Relationship,
  Entity,
  relationshipFactory,
  NounSchema,
  RelationshipSchema,
} from '../src/index';

interface ANounDefinition extends NounSchema {
  name: 'a_noun';
  namespace: 'name.space';
  metatype: 'noun';
  attributes: {
    field1: { type: 'string'; required: true };
    field2: { type: 'integer' };
    field3: { type: 'enum'; enum_def: ['a', 'b'] };
    timestampfield: { type: 'timestamp' };
    dictfield: { type: 'mapping' };
    listfield: { type: 'collection' };
    blobfield: { type: 'blob' };
  };
}

const entity_definition: ANounDefinition = {
  name: 'a_noun',
  namespace: 'name.space',
  metatype: 'noun',
  attributes: {
    field1: { type: 'string', required: true },
    field2: { type: 'integer' },
    field3: { type: 'enum', enum_def: ['a', 'b'] },
    timestampfield: { type: 'timestamp' },
    dictfield: { type: 'mapping' },
    listfield: { type: 'collection' },
    blobfield: { type: 'blob' },
  },
};

class ANoun extends Noun {
  static entity_definition: ANounDefinition = entity_definition;
  data: EntityData<ANoun>;

  constructor(obj: EntityData<ANoun>) {
    super(obj);
    let data: any = {};
    for (let attr in ANoun.entity_definition.attributes) {
      let value = this._setter(
        attr,
        obj[attr as keyof EntityData<ANoun>],
      );
      data[attr] = value;
    }
    this.data = data;
  }

  entityDefinition() {
    return ANoun.entity_definition;
  }

  public get field1(): string {
    return this.data.field1;
  }

  public set field1(v: string) {
    this.data.field1 = this._setter('field1', v);
  }

  public get field2(): number | undefined {
    return this.data.field2;
  }

  public set field2(v: number | undefined) {
    this.data.field2 = this._setter('field2', v);
  }

  public get field3(): 'a' | 'b' | undefined {
    return this.data.field3;
  }

  public set field3(v: 'a' | 'b' | undefined) {
    this.field3 = this._setter('field3', v);
  }

  public get timestampfield(): Timestamp | undefined {
    return this.data.timestampfield;
  }

  public set timestampfield(v: Timestamp | undefined) {
    this.data.timestampfield = this._setter('timestampfield', v);
  }

  public get dictfield(): Mapping | undefined {
    return this.data.dictfield;
  }

  public set dictfield(v: Mapping | undefined) {
    this.data.dictfield = this._setter('dictfield', v);
  }

  public get listfield(): Collection | undefined {
    return this.data.listfield;
  }

  public set listfield(v: Collection | undefined) {
    this.data.listfield = this._setter('listfield', v);
  }

  public get blobfield(): string | undefined {
    return this.data.blobfield;
  }

  public set blobfield(v: string | undefined) {
    this.data.blobfield = this._setter('blobfield', v);
  }
}

interface ARelationshipDefinition extends RelationshipSchema {
  attributes: {
    field1: { type: 'string'; required: true };
    field2: { type: 'integer' };
    field3: { type: 'enum'; enum_def: ['a', 'b'] };
  };
}
const rel_definition: ARelationshipDefinition = {
  name: 'a_relationship',
  namespace: 'name.space',
  metatype: 'relationship',
  attributes: {
    field1: { type: 'string', required: true },
    field2: { type: 'integer' },
    field3: { type: 'enum', enum_def: ['a', 'b'] },
  },
  ref_from: 'name.space.a_noun',
  ref_to: 'name.space.a_noun',
};

class ARelationship extends Relationship {
  entityDefinition() {
    return ARelationship.entity_definition;
  }
  protected data: EntityData<ARelationship>;
  static entity_definition: ARelationshipDefinition = rel_definition;

  constructor(
    obj: EntityData<ARelationship>,
    ref_from: string,
    ref_to: string,
  ) {
    super(obj, ref_from, ref_to);
    let data: any = {};
    for (let attr in ARelationship.entity_definition.attributes) {
      let value = this._setter(
        attr,
        obj[attr as keyof EntityData<ARelationship>],
      );
      data[attr] = value;
    }
    this.data = data;
  }

  public get field1(): string {
    return this.data.field1;
  }

  public set field1(v: string) {
    this.data.field1 = this._setter('field1', v);
  }

  public get field2(): number | undefined {
    return this.data.field2;
  }

  public set field2(v: number | undefined) {
    this.data.field2 = this._setter('field2', v);
  }

  public get field3(): 'a' | 'b' | undefined {
    return this.data.field3;
  }

  public set field3(v: 'a' | 'b' | undefined) {
    this.field3 = this._setter('field3', v);
  }
}
describe('Noun', () => {
  let anoun: ANoun;
  beforeAll(() => {
    anoun = new ANoun({
      field1: 'test',
      field2: 2,
      field3: 'a',
      timestampfield: '2020-01-01T00:00:00.000',
      dictfield: { test: 'any' },
      listfield: ['any', 2],
      blobfield: 'bigblob',
    });
  });
  it('should have namespaced name', () => {
    expect(anoun.namespaceName).toBe('name.space.a_noun');
  });
  it('should return field values', () => {
    expect(anoun.field1).toBe('test');
    expect(anoun.field2).toBe(2);
    expect(anoun.field3).toBe('a');
    expect(anoun.timestampfield).toBe('2020-01-01T00:00:00.000Z');
    expect(anoun.dictfield).toEqual({ test: 'any' });
    expect(anoun.listfield).toEqual(['any', 2]);
    expect(anoun.blobfield).toEqual('bigblob');
  });
  it('should serialize properly', () => {
    expect(anoun.serialize()).toEqual({
      field1: 'test',
      field2: 2,
      field3: 'a',
      timestampfield: '2020-01-01T00:00:00.000Z',
      dictfield: btoa(JSON.stringify({ test: 'any' })),
      listfield: btoa(JSON.stringify(['any', 2])),
      blobfield: btoa('bigblob'),
    });
    expect(anoun.serialize({ includeSchema: true }).__schema).toEqual(
      'name.space.a_noun',
    );
    expect(
      anoun.serialize({ encodeBlobs: false })['dictfield'],
    ).toEqual({ test: 'any' });
  });
  it('should deserialize properly', () => {
    const serialized = anoun.serialize();
    expect(Entity.deserialize(entity_definition, serialized)).toEqual(
      anoun,
    );
  });
  it('should set identifier', () => {
    anoun.identifier = 'test';
    expect(anoun.identifier).toBe('test');
  });
  it('should not accept invalid dates', () => {
    expect(() => (anoun.timestampfield = 'test')).toThrow(
      'Invalid date format for timestampfield',
    );
    anoun.timestampfield = undefined;
    expect(anoun.timestampfield).toBeUndefined();
  });
  it('should convert timestamps to UTC', () => {
    anoun.timestampfield = parseTimestamp(
      '2021-01-01T00:00:00.000-05:00',
    );
    expect(anoun.timestampfield).toEqual('2021-01-01T05:00:00.000Z');
  });
  it('should accept same Noun to setEquals', () => {
    const noun2 = new ANoun({
      identifier: anoun.identifier,
      field1: 'foobar',
      field2: 3,
      field3: 'b',
    });

    anoun.setEquals(noun2);

    expect(anoun).not.toBe(noun2);
    expect(anoun.field1).toBe('foobar');
    expect(anoun.field2).toBe(3);
    expect(anoun.field3).toBe('b');
    expect(anoun.timestampfield).toBeUndefined();
    expect(anoun.dictfield).toBeUndefined();
    expect(anoun.listfield).toBeUndefined();
    expect(anoun.blobfield).toBeUndefined();
  });
});

describe('Noun Factory', () => {
  let genNoun: ReturnType<typeof nounFactory>;
  beforeAll(() => {
    genNoun = nounFactory(entity_definition, {
      field1: 'test',
      field2: 2,
      field3: 'a',
      timestampfield: '2020-01-01T00:00:00.000',
      dictfield: { test: 'any' },
      listfield: ['any', 2],
      blobfield: 'bigblob',
    });
  });
  it('should have namespaced name', () => {
    expect(genNoun.namespaceName).toBe('name.space.a_noun');
  });
  it('should return field values', () => {
    expect(genNoun.field1).toBe('test');
    expect(genNoun.field2).toBe(2);
    expect(genNoun.field3).toBe('a');
    expect(genNoun.timestampfield).toBe('2020-01-01T00:00:00.000Z');
    expect(genNoun.dictfield).toEqual({ test: 'any' });
    expect(genNoun.listfield).toEqual(['any', 2]);
    expect(genNoun.blobfield).toEqual('bigblob');
  });
  it('should serialize properly', () => {
    expect(genNoun.serialize()).toEqual({
      field1: 'test',
      field2: 2,
      field3: 'a',
      timestampfield: '2020-01-01T00:00:00.000Z',
      dictfield: btoa(JSON.stringify({ test: 'any' })),
      listfield: btoa(JSON.stringify(['any', 2])),
      blobfield: btoa('bigblob'),
    });
  });
  it('should set identifier', () => {
    genNoun.identifier = 'test';
    expect(genNoun.identifier).toBe('test');
  });
  it('should not allow invalid types', () => {
    expect(() => (genNoun.field2 = 'test')).toThrow(
      'Invalid type for "field2", must be integer',
    );
    expect(() => (genNoun.dictfield = [])).toThrow(
      'Field, dictfield, must be an object',
    );
    expect(() => (genNoun.listfield = {})).toThrow(
      'Field, listfield, must be an array',
    );
    expect(() => (genNoun.field3 = 'test')).toThrow(
      'Field, field3, must be one of a, b',
    );
    expect(() => (genNoun.field1 = { test: 'any' })).toThrow(
      'Invalid type for "field1", must be string',
    );
  });
  it('should not allow required fields to be undefined', () => {
    expect(() => (genNoun.field1 = undefined)).toThrow(
      'Required field, field1, cannot be undefined',
    );
  });
  it('should set field values', () => {
    genNoun.field1 = 'test again';
    expect(genNoun.field1).toBe('test again');
  });
  it('should not allow missing fields', () => {
    expect(() => nounFactory(entity_definition, {})).toThrow(
      'Missing required fields: field1',
    );
  });
  it('should not allow extra fields', () => {
    expect(() =>
      nounFactory(entity_definition, {
        field1: 'dummy',
        extra: 'field',
      }),
    ).toThrow('Extra fields found: extra');
  });
});

describe('Relationship', () => {
  let arel: ARelationship;
  let a1: string;
  let a2: string;
  beforeAll(() => {
    a1 = 'noun1';
    a2 = 'noun2';
    arel = new ARelationship(
      {
        field1: 'test',
        field2: 2,
        field3: 'a',
      },
      a1,
      a2,
    );
  });
  it('should have namespaced name', () => {
    expect(arel.namespaceName).toBe('name.space.a_relationship');
  });
  it('should return field values', () => {
    expect(arel.field1).toBe('test');
    expect(arel.field2).toBe(2);
    expect(arel.field3).toBe('a');
  });
  it('should serialize properly', () => {
    expect(arel.serialize()).toEqual({
      field1: 'test',
      field2: 2,
      field3: 'a',
      ref_from: a1,
      ref_to: a2,
    });
    expect(arel.serialize({ includeSchema: true }).__schema).toEqual(
      'name.space.a_relationship',
    );
  });
  it('should deserialize properly', () => {
    const serialized = arel.serialize();
    expect(Entity.deserialize(rel_definition, serialized)).toEqual(
      arel,
    );
  });
  it('should set identifier', () => {
    arel.identifier = 'test';
    expect(arel.identifier).toBe('test');
  });
  it('should have from/to refs', () => {
    expect(arel.refFrom).toEqual(a1);
    expect(arel.refTo).toEqual(a2);
  });
  it('should accept same Realtionship to setEquals', () => {
    const rel2 = new ARelationship(
      {
        identifier: arel.identifier,
        field1: 'foobar',
        field2: 3,
        field3: 'b',
      },
      a1,
      a2,
    );

    arel.setEquals(rel2);

    expect(arel).not.toBe(rel2);
    expect(arel.field1).toBe('foobar');
    expect(arel.field2).toBe(3);
    expect(arel.field3).toBe('b');
  });
});

describe('Relationship Factory', () => {
  let genRel: ReturnType<typeof relationshipFactory>;
  let a1: string;
  let a2: string;
  beforeAll(() => {
    a1 = 'noun1';
    a2 = 'noun2';
    genRel = relationshipFactory(
      rel_definition,
      {
        field1: 'test',
        field2: 2,
        field3: 'a',
      },
      a1,
      a2,
    );
  });
  it('should have namespaced name', () => {
    expect(genRel.namespaceName).toBe('name.space.a_relationship');
  });
  it('should return field values', () => {
    expect(genRel.field1).toBe('test');
    expect(genRel.field2).toBe(2);
    expect(genRel.field3).toBe('a');
  });
  it('should serialize properly', () => {
    expect(genRel.serialize()).toEqual({
      field1: 'test',
      field2: 2,
      field3: 'a',
      ref_from: a1,
      ref_to: a2,
    });
  });
  it('should set identifier', () => {
    genRel.identifier = 'test';
    expect(genRel.identifier).toBe('test');
  });
  it('should have from/to refs', () => {
    expect(genRel.refFrom).toEqual(a1);
    expect(genRel.refTo).toEqual(a2);
  });
});
