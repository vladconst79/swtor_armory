export type FieldKind = 'boolean' | 'date' | 'number' | 'text'

export type ResourceField = {
  source: string
  label?: string
  kind?: FieldKind
  required?: boolean
  readOnly?: boolean
}

export type ResourceDefinition = {
  name: string
  label: string
  adminManaged?: boolean
  fields: ResourceField[]
}

export const resources: ResourceDefinition[] = [
  {
    name: 'characters',
    label: 'Characters',
    fields: [
      { source: 'id', kind: 'number', readOnly: true },
      { source: 'name', required: true },
      { source: 'faction', required: true },
      { source: 'server' },
      { source: 'level', kind: 'number' },
      { source: 'owner_id', label: 'Owner', kind: 'number', readOnly: true },
      { source: 'active', kind: 'boolean' },
    ],
  },
  {
    name: 'items',
    label: 'Items',
    fields: [
      { source: 'id', kind: 'number', readOnly: true },
      { source: 'name', required: true },
      { source: 'rarity' },
      { source: 'binding' },
      { source: 'cargo_hold', label: 'Cargo Hold' },
      { source: 'cargo_bay', label: 'Bay', kind: 'number' },
      { source: 'owner_id', label: 'Owner', kind: 'number', readOnly: true },
      { source: 'active', kind: 'boolean' },
    ],
  },
  {
    name: 'loadouts',
    label: 'Loadouts',
    fields: [
      { source: 'id', kind: 'number', readOnly: true },
      { source: 'name', required: true },
      { source: 'loadout_type', label: 'Type', required: true },
      { source: 'owner_id', label: 'Owner', kind: 'number', readOnly: true },
      { source: 'active', kind: 'boolean' },
    ],
  },
  {
    name: 'crew-skills',
    label: 'Crew Skills',
    adminManaged: true,
    fields: [
      { source: 'id', kind: 'number', readOnly: true },
      { source: 'name', required: true },
      { source: 'skill_type', label: 'Type', required: true },
      { source: 'active', kind: 'boolean' },
    ],
  },
  {
    name: 'character-crew-skill-relations',
    label: 'Character Crew Skills',
    fields: [
      { source: 'id', kind: 'number', readOnly: true },
      { source: 'display_name', label: 'Display Name', readOnly: true },
      { source: 'character_id', label: 'Character', kind: 'number' },
      { source: 'crew_skill_id', label: 'Crew Skill', kind: 'number' },
      { source: 'level', kind: 'number' },
      { source: 'progress', kind: 'number', readOnly: true },
      { source: 'active', kind: 'boolean' },
    ],
  },
  {
    name: 'operations',
    label: 'Operations',
    adminManaged: true,
    fields: [
      { source: 'id', kind: 'number', readOnly: true },
      { source: 'name', required: true },
      { source: 'short_name', label: 'Short Name' },
      { source: 'active', kind: 'boolean' },
    ],
  },
  {
    name: 'operation-lockouts',
    label: 'Lockouts',
    fields: [
      { source: 'id', kind: 'number', readOnly: true },
      { source: 'name', readOnly: true },
      { source: 'week', kind: 'date' },
      { source: 'faction', readOnly: true },
      { source: 'completion_rate', label: 'Complete %', kind: 'number', readOnly: true },
      { source: 'owner_id', label: 'Owner', kind: 'number', readOnly: true },
    ],
  },
  {
    name: 'class-names',
    label: 'Classes',
    adminManaged: true,
    fields: [
      { source: 'id', kind: 'number', readOnly: true },
      { source: 'name', required: true },
      { source: 'power_type', label: 'Power Type', required: true },
      { source: 'active', kind: 'boolean' },
    ],
  },
  {
    name: 'origin-stories',
    label: 'Origin Stories',
    adminManaged: true,
    fields: [
      { source: 'id', kind: 'number', readOnly: true },
      { source: 'name', required: true },
      { source: 'power_type', label: 'Power Type', required: true },
      { source: 'active', kind: 'boolean' },
    ],
  },
  {
    name: 'roles',
    label: 'Roles',
    adminManaged: true,
    fields: [
      { source: 'id', kind: 'number', readOnly: true },
      { source: 'name', required: true },
      { source: 'color', kind: 'number' },
      { source: 'active', kind: 'boolean' },
    ],
  },
  {
    name: 'specs',
    label: 'Specs',
    adminManaged: true,
    fields: [
      { source: 'id', kind: 'number', readOnly: true },
      { source: 'name', required: true },
      { source: 'role_id', label: 'Role', kind: 'number' },
      { source: 'class_name_id', label: 'Class', kind: 'number' },
      { source: 'mirror_spec_id', label: 'Mirror Spec', kind: 'number' },
      { source: 'active', kind: 'boolean' },
    ],
  },
  {
    name: 'titles',
    label: 'Titles',
    adminManaged: true,
    fields: [
      { source: 'id', kind: 'number', readOnly: true },
      { source: 'name', required: true },
      { source: 'source' },
      { source: 'type' },
      { source: 'active', kind: 'boolean' },
    ],
  },
  {
    name: 'vehicles',
    label: 'Mounts',
    adminManaged: true,
    fields: [
      { source: 'id', kind: 'number', readOnly: true },
      { source: 'name', required: true },
      { source: 'source' },
      { source: 'bind' },
      { source: 'active', kind: 'boolean' },
    ],
  },
  {
    name: 'guilds',
    label: 'Guilds',
    adminManaged: true,
    fields: [
      { source: 'id', kind: 'number', readOnly: true },
      { source: 'name', required: true },
      { source: 'guildmaster' },
      { source: 'member_count', label: 'Members', kind: 'number' },
      { source: 'active', kind: 'boolean' },
    ],
  },
]
