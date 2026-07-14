import {
  AutocompleteArrayInput,
  AutocompleteInput,
  BooleanField,
  BooleanInput,
  Create,
  Datagrid,
  DeleteButton,
  Edit,
  EditButton,
  List,
  NumberField,
  NumberInput,
  ReferenceArrayInput,
  ReferenceField,
  ReferenceInput,
  SearchInput,
  Show,
  ShowButton,
  SimpleForm,
  SimpleShowLayout,
  TextField,
  required,
  type RaRecord,
} from 'react-admin'

const relationFilters = [
  <SearchInput key="q" source="q" alwaysOn />,
  <BooleanInput key="mine" source="mine" label="My crew skills" />,
  <ReferenceArrayInput key="character_ids" source="character_ids" reference="characters" label="Characters">
    <AutocompleteArrayInput optionText="name" />
  </ReferenceArrayInput>,
  <ReferenceArrayInput key="crew_skill_ids" source="crew_skill_ids" reference="crew-skills" label="Crew Skills">
    <AutocompleteArrayInput optionText="name" />
  </ReferenceArrayInput>,
]

const RelationRowActions = ({ record }: { record?: RaRecord }) => (
  <>
    <ShowButton record={record} />
    <EditButton record={record} />
    <DeleteButton record={record} mutationMode="pessimistic" />
  </>
)

const CharacterCrewSkillForm = () => (
  <SimpleForm>
    <ReferenceInput source="character_id" reference="characters" label="Character">
      <AutocompleteInput optionText="name" validate={[required()]} />
    </ReferenceInput>
    <ReferenceInput source="crew_skill_id" reference="crew-skills" label="Crew Skill">
      <AutocompleteInput optionText="name" validate={[required()]} />
    </ReferenceInput>
    <NumberInput source="level" min={1} max={700} validate={[required()]} />
    <BooleanInput source="active" />
  </SimpleForm>
)

export const CharacterCrewSkillList = () => (
  <List filters={relationFilters} perPage={25} sort={{ field: 'display_name', order: 'ASC' }}>
    <Datagrid bulkActionButtons={false} rowClick="show">
      <TextField source="display_name" label="Display Name" />
      <ReferenceField source="character_id" reference="characters" label="Character" />
      <ReferenceField source="crew_skill_id" reference="crew-skills" label="Crew Skill" />
      <TextField source="skill_type" label="Type" />
      <NumberField source="level" />
      <NumberField source="progress" />
      <BooleanField source="active" />
      <RelationRowActions />
    </Datagrid>
  </List>
)

export const CharacterCrewSkillShow = () => (
  <Show>
    <SimpleShowLayout>
      <TextField source="display_name" label="Display Name" />
      <ReferenceField source="character_id" reference="characters" label="Character" />
      <ReferenceField source="crew_skill_id" reference="crew-skills" label="Crew Skill" />
      <TextField source="skill_type" label="Type" />
      <NumberField source="level" />
      <NumberField source="progress" />
      <BooleanField source="active" />
    </SimpleShowLayout>
  </Show>
)

export const CharacterCrewSkillCreate = () => (
  <Create>
    <CharacterCrewSkillForm />
  </Create>
)

export const CharacterCrewSkillEdit = () => (
  <Edit>
    <CharacterCrewSkillForm />
  </Edit>
)
