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

const ClassNameFields = () => (
  <>
    <TextField source="name" />
    <TextField source="power_type" label="Power Type" />
    <ReferenceArrayField source="role_ids" reference="roles" label="Roles">
      <SingleFieldList linkType={false}>
        <ChipField source="name" />
      </SingleFieldList>
    </ReferenceArrayField>
    <BooleanField source="active" />
  </>
)

const OriginStoryFields = () => (
  <>
    <TextField source="name" />
    <TextField source="power_type" label="Power Type" />
    <BooleanField source="active" />
  </>
)

const RoleFields = () => (
  <>
    <TextField source="name" />
    <NumberField source="color" />
    <ReferenceArrayField source="class_name_ids" reference="class-names" label="Classes">
      <SingleFieldList linkType={false}>
        <ChipField source="name" />
      </SingleFieldList>
    </ReferenceArrayField>
    <BooleanField source="active" />
  </>
)

const SpecFields = () => (
  <>
    <TextField source="name" />
    <ReferenceField source="class_name_id" reference="class-names" label="Class" />
    <ReferenceField source="role_id" reference="roles" label="Role" />
    <ReferenceField source="mirror_spec_id" reference="specs" label="Mirror Spec" />
    <BooleanField source="active" />
  </>
)

const TitleFields = () => (
  <>
    <TextField source="name" />
    <TextField source="source" />
    <TextField source="type" />
    <ReferenceField source="operation_id" reference="operations" label="Operation" />
    <ReferenceField source="operation_difficulty_id" reference="operation-difficulties" label="Difficulty" />
    <TextField source="icon_url" label="Icon URL" />
    <BooleanField source="active" />
  </>
)

const VehicleFields = () => (
  <>
    <TextField source="name" />
    <TextField source="source" />
    <TextField source="bind" />
    <ReferenceField source="operation_id" reference="operations" label="Operation" />
    <ReferenceField source="operation_difficulty_id" reference="operation-difficulties" label="Difficulty" />
    <TextField source="icon_url" label="Icon URL" />
    <BooleanField source="active" />
  </>
)

const GuildFields = () => (
  <>
    <TextField source="name" />
    <TextField source="guildmaster" />
    <NumberField source="member_count" label="Members" />
    <TextField source="description" />
    <BooleanField source="active" />
  </>
)

const ReferenceFields = ({ kind }: { kind: ReferenceFormKind }) => {
  if (kind === 'class') return <ClassNameFields />
  if (kind === 'origin') return <OriginStoryFields />
  if (kind === 'role') return <RoleFields />
  if (kind === 'spec') return <SpecFields />
  if (kind === 'title') return <TitleFields />
  if (kind === 'vehicle') return <VehicleFields />
  return <GuildFields />
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
      <ReferenceFields kind={kind} />
      <ReferenceRowActions />
    </Datagrid>
  </List>
)

const ReferenceShowBase = ({ kind }: { kind: ReferenceFormKind }) => (
  <Show>
    <SimpleShowLayout>
      <ReferenceFields kind={kind} />
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
