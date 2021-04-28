import { EntityDefinition, EntityInput, Noun } from '../src/index';

interface ANounDefinition extends EntityDefinition {
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

class ANoun extends Noun {
  static entity_definition: ANounDefinition = {
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
  data: EntityInput<ANoun>;

  constructor(obj: EntityInput<ANoun>) {
    super(obj);
    this.data = obj;
  }

  entityDefinition() {
    return ANoun.entity_definition;
  }

  public get field1(): string {
    return this.data.field1;
  }

  public set field1(v: string) {
    this.data.field1 = v;
  }

  public get field2(): number | undefined {
    return this.data.field2;
  }

  public set field2(v: number | undefined) {
    this.data.field2 = v;
  }

  public get field3(): 'a' | 'b' | undefined {
    return this.data.field3;
  }

  public set field3(v: 'a' | 'b' | undefined) {
    this.field3 = v;
  }

  public get timestampfield(): string | undefined {
    return this.data.timestampfield;
  }

  public set timestampfield(v: string | undefined) {
    this.data.timestampfield = v;
  }

  public get dictfield(): { [k: string]: any } | undefined {
    return this.data.dictfield;
  }

  public set dictfield(v: { [k: string]: any } | undefined) {
    this.data.dictfield = v;
  }

  public get listfield(): any[] | undefined {
    return this.data.listfield;
  }

  public set listfield(v: any[] | undefined) {
    this.data.listfield = v;
  }

  public get blobfield(): string | undefined {
    return this.data.blobfield;
  }

  public set blobfield(v: string | undefined) {
    this.data.blobfield = v;
  }
}

describe('Noun', () => {
  let anoun: ANoun;
  beforeAll(() => {
    anoun = new ANoun({
      field1: 'test',
      field2: 2,
      field3: 'a',
      timestampfield: '2020-01-01T00:00.000z',
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
    expect(anoun.timestampfield).toBe('2020-01-01T00:00.000z');
    expect(anoun.dictfield).toEqual({ test: 'any' });
    expect(anoun.listfield).toEqual(['any', 2]);
    expect(anoun.blobfield).toEqual('bigblob');
  });
  it('should serialize properly', () => {
    expect(anoun.serialize()).toEqual({
      field1: 'test',
      field2: 2,
      field3: 'a',
      timestampfield: '2020-01-01T00:00.000z',
      dictfield: btoa(JSON.stringify({ test: 'any' })),
      listfield: btoa(JSON.stringify(['any', 2])),
      blobfield: btoa(JSON.stringify('bigblob')),
    });
  });
  it('should set identifier', () => {
    anoun.identifier = 'test';
    expect(anoun.identifier).toBe('test');
  });
});
