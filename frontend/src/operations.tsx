import {
  AutocompleteArrayInput,
  AutocompleteInput,
  BooleanField,
  BooleanInput,
  ChipField,
  Create,
  Datagrid,
  DateField,
  DateInput,
  DeleteButton,
  Edit,
  EditButton,
  FunctionField,
  List,
  NumberField,
  ReferenceArrayField,
  ReferenceArrayInput,
  ReferenceField,
  ReferenceInput,
  SearchInput,
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

const operationFilters = [
  <SearchInput key="q" source="q" alwaysOn />,
  <ReferenceArrayInput key="difficulty_ids" source="difficulty_ids" reference="operation-difficulties" label="Difficulties">
    <AutocompleteArrayInput optionText="name" />
  </ReferenceArrayInput>,
  <BooleanInput key="active" source="active" />,
]

const lockoutFilters = [
  <BooleanInput key="current_week" source="current_week" label="Current week" alwaysOn />,
  <BooleanInput key="mine" source="mine" label="My lockouts" />,
  <ReferenceArrayInput key="character_ids" source="character_ids" reference="characters" label="Characters">
    <AutocompleteArrayInput optionText="name" />
  </ReferenceArrayInput>,
  <ReferenceArrayInput key="operation_ids" source="operation_ids" reference="operations" label="Operations">
    <AutocompleteArrayInput optionText="name" />
  </ReferenceArrayInput>,
  <ReferenceArrayInput
    key="difficulty_ids"
    source="difficulty_ids"
    reference="operation-difficulties"
    label="Difficulties"
  >
    <AutocompleteArrayInput optionText="name" />
  </ReferenceArrayInput>,
]

const OperationRowActions = ({ record }: { record?: RaRecord }) => (
  <>
    <ShowButton record={record} />
    <EditButton record={record} />
    <DeleteButton record={record} mutationMode="pessimistic" />
  </>
)

const LockoutRowActions = ({ record }: { record?: RaRecord }) => (
  <>
    <ShowButton record={record} />
    <EditButton record={record} />
    <DeleteButton record={record} mutationMode="pessimistic" />
  </>
)

const OperationForm = () => (
  <SimpleForm>
    <TextInput source="name" validate={[required()]} fullWidth />
    <TextInput source="short_name" label="Short Name" />
    <ReferenceArrayInput source="difficulty_ids" reference="operation-difficulties" label="Difficulties">
      <AutocompleteArrayInput optionText="name" />
    </ReferenceArrayInput>
    <BooleanInput source="active" />
  </SimpleForm>
)

const OperationLockoutForm = () => (
  <SimpleForm>
    <DateInput source="week" validate={[required()]} />
    <ReferenceInput source="character_id" reference="characters" label="Character">
      <AutocompleteInput optionText="name" validate={[required()]} />
    </ReferenceInput>
    <ReferenceInput source="operation_id" reference="operations" label="Operation">
      <AutocompleteInput optionText="name" validate={[required()]} />
    </ReferenceInput>
    <ReferenceInput source="boss_id" reference="operation-bosses" label="Boss">
      <AutocompleteInput optionText="name" validate={[required()]} />
    </ReferenceInput>
    <ReferenceInput source="difficulty_id" reference="operation-difficulties" label="Difficulty">
      <AutocompleteInput optionText="name" validate={[required()]} />
    </ReferenceInput>
    <BooleanInput source="active" />
  </SimpleForm>
)

export const OperationList = () => (
  <List filters={operationFilters} perPage={25} sort={{ field: 'name', order: 'ASC' }}>
    <Datagrid bulkActionButtons={false} rowClick="show">
      <TextField source="name" />
      <TextField source="short_name" label="Short Name" />
      <ReferenceArrayField source="difficulty_ids" reference="operation-difficulties" label="Difficulties">
        <SingleFieldList linkType={false}>
          <ChipField source="name" />
        </SingleFieldList>
      </ReferenceArrayField>
      <BooleanField source="active" />
      <OperationRowActions />
    </Datagrid>
  </List>
)

export const OperationShow = () => (
  <Show>
    <SimpleShowLayout>
      <TextField source="name" />
      <TextField source="short_name" label="Short Name" />
      <ReferenceArrayField source="difficulty_ids" reference="operation-difficulties" label="Difficulties">
        <SingleFieldList linkType={false}>
          <ChipField source="name" />
        </SingleFieldList>
      </ReferenceArrayField>
      <BooleanField source="active" />
    </SimpleShowLayout>
  </Show>
)

export const OperationCreate = () => (
  <Create>
    <OperationForm />
  </Create>
)

export const OperationEdit = () => (
  <Edit>
    <OperationForm />
  </Edit>
)

export const OperationLockoutList = () => (
  <List
    filters={lockoutFilters}
    filterDefaultValues={{ current_week: true }}
    perPage={25}
    sort={{ field: 'week', order: 'DESC' }}
  >
    <Datagrid bulkActionButtons={false} rowClick="show">
      <TextField source="name" />
      <DateField source="week" />
      <ReferenceField source="character_id" reference="characters" label="Character" />
      <ReferenceField source="operation_id" reference="operations" label="Operation" />
      <ReferenceField source="boss_id" reference="operation-bosses" label="Boss" />
      <ReferenceField source="difficulty_id" reference="operation-difficulties" label="Difficulty" />
      <TextField source="faction" />
      <NumberField source="completion_rate" label="Complete %" />
      <LockoutRowActions />
    </Datagrid>
  </List>
)

export const OperationLockoutShow = () => (
  <Show>
    <SimpleShowLayout>
      <TextField source="name" />
      <DateField source="week" />
      <ReferenceField source="character_id" reference="characters" label="Character" />
      <ReferenceField source="operation_id" reference="operations" label="Operation" />
      <ReferenceField source="boss_id" reference="operation-bosses" label="Boss" />
      <ReferenceField source="difficulty_id" reference="operation-difficulties" label="Difficulty" />
      <TextField source="faction" />
      <NumberField source="completion_rate" label="Complete %" />
      <FunctionField source="active" render={(record) => (record.active ? 'Active' : 'Inactive')} />
    </SimpleShowLayout>
  </Show>
)

export const OperationLockoutCreate = () => (
  <Create>
    <OperationLockoutForm />
  </Create>
)

export const OperationLockoutEdit = () => (
  <Edit>
    <OperationLockoutForm />
  </Edit>
)
