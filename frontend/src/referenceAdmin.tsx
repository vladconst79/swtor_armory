import {
  AutocompleteArrayInput,
  AutocompleteInput,
  BooleanField,
  BooleanInput,
  ChipField,
  Create,
  Datagrid,
  DeleteButton,
  Edit,
  EditButton,
  List,
  NumberField,
  NumberInput,
  ReferenceArrayField,
  ReferenceArrayInput,
  ReferenceField,
  ReferenceInput,
  SearchInput,
  SelectInput,
  Show,
  ShowButton,
  SimpleForm,
  SimpleShowLayout,
  SingleFieldList,
  TextField,
  TextInput,
  required,
  usePermissions,
  type RaRecord,
} from 'react-admin'

type ReferenceFormKind = 'class' | 'guild' | 'origin' | 'role' | 'spec' | 'title' | 'vehicle'
const powerTypeChoices = [
  { id: 'force', name: 'Force' },
  { id: 'tech', name: 'Tech' },
]

const titleSourceChoices = [
  { id: 'operation', name: 'Operation' },
  { id: 'flashpoint', name: 'Flashpoint' },
  { id: 'pvp', name: 'PvP' },
  { id: 'pve', name: 'PvE' },
  { id: 'space', name: 'Space' },
  { id: 'cartel', name: 'Cartel' },
  { id: 'reputation', name: 'Reputation' },
  { id: 'crafting', name: 'Crafting' },
  { id: 'event', name: 'Event' },
  { id: 'promotion', name: 'Promotion' },
  { id: 'subscription', name: 'Subscription' },
]

const vehicleSourceChoices = [
  ...titleSourceChoices,
  { id: 'world_boss', name: 'World Boss' },
  { id: 'vendor', name: 'Vendor' },
]

const titleTypeChoices = [
  { id: 'legacy', name: 'Legacy' },
  { id: 'character', name: 'Character' },
]

const vehicleBindChoices = [
  { id: 'bind_on_pickup', name: 'Bind on Pickup' },
  { id: 'bind_on_equip', name: 'Bind on Equip' },
  { id: 'bind_on_legacy', name: 'Bind on Legacy' },
]

const referenceFilters = [
  <SearchInput key="q" source="q" alwaysOn />,
  <BooleanInput key="active" source="active" />,
]

const ReferenceRowActions = ({ record }: { record?: RaRecord }) => {
  const { permissions } = usePermissions()
  const writable = permissions === 'admin'

  return (
    <>
      <ShowButton record={record} />
      {writable ? <EditButton record={record} /> : null}
      {writable ? <DeleteButton record={record} mutationMode="pessimistic" /> : null}
    </>
  )
}

const classNameFields = [
  <TextField key="name" source="name" />,
  <TextField key="power_type" source="power_type" label="Power Type" />,
  <ReferenceArrayField key="role_ids" source="role_ids" reference="roles" label="Roles">
    <SingleFieldList linkType={false}>
      <ChipField source="name" />
    </SingleFieldList>
  </ReferenceArrayField>,
  <BooleanField key="active" source="active" />,
]

const originStoryFields = [
  <TextField key="name" source="name" />,
  <TextField key="power_type" source="power_type" label="Power Type" />,
  <BooleanField key="active" source="active" />,
]

const roleFields = [
  <TextField key="name" source="name" />,
  <NumberField key="color" source="color" />,
  <ReferenceArrayField key="class_name_ids" source="class_name_ids" reference="class-names" label="Classes">
    <SingleFieldList linkType={false}>
      <ChipField source="name" />
    </SingleFieldList>
  </ReferenceArrayField>,
  <BooleanField key="active" source="active" />,
]

const specFields = [
  <TextField key="name" source="name" />,
  <ReferenceField key="class_name_id" source="class_name_id" reference="class-names" label="Class" />,
  <ReferenceField key="role_id" source="role_id" reference="roles" label="Role" />,
  <ReferenceField key="mirror_spec_id" source="mirror_spec_id" reference="specs" label="Mirror Spec" />,
  <BooleanField key="active" source="active" />,
]

const titleFields = [
  <TextField key="name" source="name" />,
  <TextField key="source" source="source" />,
  <TextField key="type" source="type" />,
  <ReferenceField key="operation_id" source="operation_id" reference="operations" label="Operation" />,
  <ReferenceField
    key="operation_difficulty_id"
    source="operation_difficulty_id"
    reference="operation-difficulties"
    label="Difficulty"
  />,
  <TextField key="icon_url" source="icon_url" label="Icon URL" />,
  <BooleanField key="active" source="active" />,
]

const vehicleFields = [
  <TextField key="name" source="name" />,
  <TextField key="source" source="source" />,
  <TextField key="bind" source="bind" />,
  <ReferenceField key="operation_id" source="operation_id" reference="operations" label="Operation" />,
  <ReferenceField
    key="operation_difficulty_id"
    source="operation_difficulty_id"
    reference="operation-difficulties"
    label="Difficulty"
  />,
  <TextField key="icon_url" source="icon_url" label="Icon URL" />,
  <BooleanField key="active" source="active" />,
]

const guildFields = [
  <TextField key="name" source="name" />,
  <TextField key="guildmaster" source="guildmaster" />,
  <NumberField key="member_count" source="member_count" label="Members" />,
  <TextField key="description" source="description" />,
  <BooleanField key="active" source="active" />,
]

const referenceFields = (kind: ReferenceFormKind) => {
  if (kind === 'class') return classNameFields
  if (kind === 'origin') return originStoryFields
  if (kind === 'role') return roleFields
  if (kind === 'spec') return specFields
  if (kind === 'title') return titleFields
  if (kind === 'vehicle') return vehicleFields
  return guildFields
}

const ReferenceForm = ({ kind }: { kind: ReferenceFormKind }) => (
  <SimpleForm>
    <TextInput source="name" validate={[required()]} fullWidth />
    {kind === 'class' || kind === 'origin' ? (
      <SelectInput source="power_type" label="Power Type" choices={powerTypeChoices} validate={[required()]} />
    ) : null}
    {kind === 'class' ? (
      <ReferenceArrayInput source="role_ids" reference="roles" label="Roles">
        <AutocompleteArrayInput optionText="name" />
      </ReferenceArrayInput>
    ) : null}
    {kind === 'role' ? (
      <>
        <NumberInput source="color" />
        <ReferenceArrayInput source="class_name_ids" reference="class-names" label="Classes">
          <AutocompleteArrayInput optionText="name" />
        </ReferenceArrayInput>
      </>
    ) : null}
    {kind === 'spec' ? (
      <>
        <ReferenceInput source="class_name_id" reference="class-names" label="Class">
          <AutocompleteInput optionText="name" validate={[required()]} />
        </ReferenceInput>
        <ReferenceInput source="role_id" reference="roles" label="Role">
          <AutocompleteInput optionText="name" validate={[required()]} />
        </ReferenceInput>
        <ReferenceInput source="mirror_spec_id" reference="specs" label="Mirror Spec">
          <AutocompleteInput optionText="name" />
        </ReferenceInput>
      </>
    ) : null}
    {kind === 'title' ? (
      <>
        <SelectInput source="source" choices={titleSourceChoices} />
        <SelectInput source="type" choices={titleTypeChoices} />
        <ReferenceInput source="operation_id" reference="operations" label="Operation">
          <AutocompleteInput optionText="name" />
        </ReferenceInput>
        <ReferenceInput source="operation_difficulty_id" reference="operation-difficulties" label="Difficulty">
          <AutocompleteInput optionText="name" />
        </ReferenceInput>
        <TextInput source="icon_url" label="Icon URL" fullWidth />
      </>
    ) : null}
    {kind === 'vehicle' ? (
      <>
        <SelectInput source="source" choices={vehicleSourceChoices} />
        <SelectInput source="bind" choices={vehicleBindChoices} />
        <ReferenceInput source="operation_id" reference="operations" label="Operation">
          <AutocompleteInput optionText="name" />
        </ReferenceInput>
        <ReferenceInput source="operation_difficulty_id" reference="operation-difficulties" label="Difficulty">
          <AutocompleteInput optionText="name" />
        </ReferenceInput>
        <TextInput source="icon_url" label="Icon URL" fullWidth />
      </>
    ) : null}
    {kind === 'guild' ? (
      <>
        <TextInput source="guildmaster" />
        <TextInput source="description" multiline fullWidth />
      </>
    ) : null}
    <BooleanInput source="active" />
  </SimpleForm>
)

const ReferenceListBase = ({ kind, sortField = 'name' }: { kind: ReferenceFormKind; sortField?: string }) => (
  <List filters={referenceFilters} perPage={25} sort={{ field: sortField, order: 'ASC' }}>
    <Datagrid bulkActionButtons={false} rowClick="show">
      {referenceFields(kind)}
      <ReferenceRowActions />
    </Datagrid>
  </List>
)

const ReferenceShowBase = ({ kind }: { kind: ReferenceFormKind }) => (
  <Show>
    <SimpleShowLayout>
      {referenceFields(kind)}
    </SimpleShowLayout>
  </Show>
)

const ReferenceCreateBase = ({ kind }: { kind: ReferenceFormKind }) => (
  <Create>
    <ReferenceForm kind={kind} />
  </Create>
)

const ReferenceEditBase = ({ kind }: { kind: ReferenceFormKind }) => (
  <Edit>
    <ReferenceForm kind={kind} />
  </Edit>
)

export const ClassNameList = () => <ReferenceListBase kind="class" />
export const ClassNameShow = () => <ReferenceShowBase kind="class" />
export const ClassNameCreate = () => <ReferenceCreateBase kind="class" />
export const ClassNameEdit = () => <ReferenceEditBase kind="class" />

export const GuildList = () => <ReferenceListBase kind="guild" />
export const GuildShow = () => <ReferenceShowBase kind="guild" />
export const GuildCreate = () => <ReferenceCreateBase kind="guild" />
export const GuildEdit = () => <ReferenceEditBase kind="guild" />

export const OriginStoryList = () => <ReferenceListBase kind="origin" />
export const OriginStoryShow = () => <ReferenceShowBase kind="origin" />
export const OriginStoryCreate = () => <ReferenceCreateBase kind="origin" />
export const OriginStoryEdit = () => <ReferenceEditBase kind="origin" />

export const RoleList = () => <ReferenceListBase kind="role" />
export const RoleShow = () => <ReferenceShowBase kind="role" />
export const RoleCreate = () => <ReferenceCreateBase kind="role" />
export const RoleEdit = () => <ReferenceEditBase kind="role" />

export const SpecList = () => <ReferenceListBase kind="spec" />
export const SpecShow = () => <ReferenceShowBase kind="spec" />
export const SpecCreate = () => <ReferenceCreateBase kind="spec" />
export const SpecEdit = () => <ReferenceEditBase kind="spec" />

export const TitleList = () => <ReferenceListBase kind="title" />
export const TitleShow = () => <ReferenceShowBase kind="title" />
export const TitleCreate = () => <ReferenceCreateBase kind="title" />
export const TitleEdit = () => <ReferenceEditBase kind="title" />

export const VehicleList = () => <ReferenceListBase kind="vehicle" />
export const VehicleShow = () => <ReferenceShowBase kind="vehicle" />
export const VehicleCreate = () => <ReferenceCreateBase kind="vehicle" />
export const VehicleEdit = () => <ReferenceEditBase kind="vehicle" />
