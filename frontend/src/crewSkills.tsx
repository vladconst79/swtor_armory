import {
  AutocompleteArrayInput,
  BooleanField,
  BooleanInput,
  ChipField,
  Create,
  Datagrid,
  DeleteButton,
  Edit,
  EditButton,
  List,
  ReferenceArrayField,
  ReferenceArrayInput,
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

const skillTypeChoices = [
  { id: 'crafting', name: 'Crafting' },
  { id: 'gathering', name: 'Gathering' },
  { id: 'mission', name: 'Mission' },
]

const crewSkillFilters = [
  <SearchInput key="q" source="q" alwaysOn />,
  <SelectInput key="skill_type" source="skill_type" label="Type" choices={skillTypeChoices} />,
  <BooleanInput key="active" source="active" />,
]

const canWrite = (permissions: unknown) => permissions === 'admin'

const CrewSkillRowActions = ({ record }: { record?: RaRecord }) => {
  const { permissions } = usePermissions()
  const writable = canWrite(permissions)

  return (
    <>
      <ShowButton record={record} />
      {writable ? <EditButton record={record} /> : null}
      {writable ? <DeleteButton record={record} mutationMode="pessimistic" /> : null}
    </>
  )
}

const CrewSkillForm = () => (
  <SimpleForm>
    <TextInput source="name" validate={[required()]} fullWidth />
    <SelectInput source="skill_type" label="Type" choices={skillTypeChoices} validate={[required()]} />
    <ReferenceArrayInput source="related_skill_ids" reference="crew-skills" label="Related Skills">
      <AutocompleteArrayInput optionText="name" />
    </ReferenceArrayInput>
    <BooleanInput source="active" />
  </SimpleForm>
)

export const CrewSkillList = () => (
  <List filters={crewSkillFilters} perPage={25} sort={{ field: 'name', order: 'ASC' }}>
    <Datagrid bulkActionButtons={false} rowClick="show">
      <TextField source="name" />
      <TextField source="skill_type" label="Type" />
      <ReferenceArrayField source="related_skill_ids" reference="crew-skills" label="Related Skills">
        <SingleFieldList linkType={false}>
          <ChipField source="name" />
        </SingleFieldList>
      </ReferenceArrayField>
      <BooleanField source="active" />
      <CrewSkillRowActions />
    </Datagrid>
  </List>
)

export const CrewSkillShow = () => (
  <Show>
    <SimpleShowLayout>
      <TextField source="name" />
      <TextField source="skill_type" label="Type" />
      <ReferenceArrayField source="related_skill_ids" reference="crew-skills" label="Related Skills">
        <SingleFieldList linkType={false}>
          <ChipField source="name" />
        </SingleFieldList>
      </ReferenceArrayField>
      <BooleanField source="active" />
    </SimpleShowLayout>
  </Show>
)

export const CrewSkillCreate = () => (
  <Create>
    <CrewSkillForm />
  </Create>
)

export const CrewSkillEdit = () => (
  <Edit>
    <CrewSkillForm />
  </Edit>
)
