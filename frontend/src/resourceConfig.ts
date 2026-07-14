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
