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
  FunctionField,
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
  type RaRecord,
} from 'react-admin'

const loadoutTypeChoices = [
  { id: 'pve', name: 'PvE' },
  { id: 'pvp', name: 'PvP' },
]

const loadoutFilters = [
  <SearchInput key="q" source="q" alwaysOn />,
  <BooleanInput key="mine" source="mine" label="My loadouts" />,
  <SelectInput key="loadout_type" source="loadout_type" label="Type" choices={loadoutTypeChoices} />,
  <ReferenceArrayInput key="character_ids" source="character_ids" reference="characters" label="Characters">
    <AutocompleteArrayInput optionText="name" />
  </ReferenceArrayInput>,
]

const LoadoutRowActions = ({ record }: { record?: RaRecord }) => (
  <>
    <ShowButton record={record} />
    <EditButton record={record} />
    <DeleteButton record={record} mutationMode="pessimistic" />
  </>
)

const LoadoutForm = () => (
  <SimpleForm>
    <TextInput source="name" validate={[required()]} fullWidth />
    <NumberInput source="sequence" />
    <SelectInput source="loadout_type" label="Type" choices={loadoutTypeChoices} validate={[required()]} />
    <ReferenceInput source="spec_id" reference="specs" label="Spec">
      <AutocompleteInput optionText="name" />
    </ReferenceInput>
    <ReferenceArrayInput source="character_ids" reference="characters" label="Characters">
      <AutocompleteArrayInput optionText="name" />
    </ReferenceArrayInput>
    <TextInput source="loadout_url" label="Parsely URL" fullWidth />
    <TextInput source="notes" multiline fullWidth />
    <BooleanInput source="active" />
  </SimpleForm>
)

export const LoadoutList = () => (
  <List filters={loadoutFilters} perPage={25} sort={{ field: 'name', order: 'ASC' }}>
    <Datagrid bulkActionButtons={false} rowClick="show">
      <TextField source="name" />
      <TextField source="loadout_type" label="Type" />
      <ReferenceField source="spec_id" reference="specs" label="Spec" />
      <ReferenceField source="role_id" reference="roles" label="Role" />
      <ReferenceArrayField source="character_ids" reference="characters" label="Characters">
        <SingleFieldList linkType={false}>
          <ChipField source="name" />
        </SingleFieldList>
      </ReferenceArrayField>
      <BooleanField source="active" />
      <LoadoutRowActions />
    </Datagrid>
  </List>
)

export const LoadoutShow = () => (
  <Show>
    <SimpleShowLayout>
      <TextField source="name" />
      <NumberField source="sequence" />
      <TextField source="loadout_type" label="Type" />
      <ReferenceField source="spec_id" reference="specs" label="Spec" />
      <ReferenceField source="role_id" reference="roles" label="Role" />
      <ReferenceArrayField source="character_ids" reference="characters" label="Characters">
        <SingleFieldList linkType={false}>
          <ChipField source="name" />
        </SingleFieldList>
      </ReferenceArrayField>
      <TextField source="loadout_url" label="Parsely URL" />
      <FunctionField source="loadout_iframe" label="Preview URL" render={(record) => record.loadout_iframe || '-'} />
      <FunctionField source="notes" render={(record) => record.notes || '-'} />
      <BooleanField source="active" />
    </SimpleShowLayout>
  </Show>
)

export const LoadoutCreate = () => (
  <Create>
    <LoadoutForm />
  </Create>
)

export const LoadoutEdit = () => (
  <Edit>
    <LoadoutForm />
  </Edit>
)
