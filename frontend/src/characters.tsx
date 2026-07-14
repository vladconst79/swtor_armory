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
  TopToolbar,
  required,
  useListContext,
  type RaRecord,
} from 'react-admin'

const factionChoices = [
  { id: 'republic', name: 'Republic' },
  { id: 'empire', name: 'Empire' },
]

const genderChoices = [
  { id: 'female', name: 'Female' },
  { id: 'male', name: 'Male' },
]

const characterFilters = [
  <SearchInput key="q" source="q" alwaysOn />,
  <BooleanInput key="mine" source="mine" label="My characters" />,
  <SelectInput key="faction" source="faction" choices={factionChoices} />,
  <TextInput key="server" source="server" />,
  <TextInput key="guild" source="guild" />,
  <ReferenceArrayInput key="role_ids" source="role_ids" reference="roles" label="Roles">
    <AutocompleteArrayInput optionText="name" />
  </ReferenceArrayInput>,
]

const CharacterListActions = () => (
  <TopToolbar>
    <EditButton />
  </TopToolbar>
)

const CharacterRowActions = ({ record }: { record?: RaRecord }) => (
  <>
    <ShowButton record={record} />
    <EditButton record={record} />
    <DeleteButton record={record} mutationMode="pessimistic" />
  </>
)

const CharacterCards = () => {
  const { data, isPending } = useListContext()
  const records = Object.values(data ?? {})

  if (isPending || records.length === 0) {
    return null
  }

  return (
    <section className="character-card-board" aria-label="Character card view">
      {records.map((record) => (
        <article key={record.id} className="character-card">
          <div className="character-card__header">
            <div>
              <h3>{record.display_name || record.name}</h3>
              <p>{record.server || 'No server'}</p>
            </div>
            <span>{record.faction}</span>
          </div>
          <dl>
            <div>
              <dt>Level</dt>
              <dd>{record.level ?? '-'}</dd>
            </div>
            <div>
              <dt>Valor</dt>
              <dd>{record.valor_rank ?? '-'}</dd>
            </div>
            <div>
              <dt>Roles</dt>
              <dd>{record.role_ids?.length ?? 0}</dd>
            </div>
            <div>
              <dt>Crew</dt>
              <dd>{record.crew_skills_count ?? 0}</dd>
            </div>
          </dl>
          <div className="character-card__actions">
            <ShowButton record={record} />
            <EditButton record={record} />
          </div>
        </article>
      ))}
    </section>
  )
}

const CharacterForm = () => (
  <SimpleForm>
    <TextInput source="name" validate={[required()]} fullWidth />
    <SelectInput source="faction" choices={factionChoices} validate={[required()]} />
    <ReferenceInput source="origin_story_id" reference="origin-stories" label="Origin Story">
      <AutocompleteInput optionText="name" />
    </ReferenceInput>
    <NumberInput source="level" min={1} max={80} />
    <NumberInput source="valor_rank" label="Valor Rank" min={1} max={100} />
    <TextInput source="server" />
    <TextInput source="guild" />
    <TextInput source="race" />
    <SelectInput source="gender" choices={genderChoices} />
    <TextInput source="alignment" />
    <ReferenceArrayInput source="class_name_ids" reference="class-names" label="Classes">
      <AutocompleteArrayInput optionText="name" />
    </ReferenceArrayInput>
    <ReferenceArrayInput source="role_ids" reference="roles" label="Roles">
      <AutocompleteArrayInput optionText="name" />
    </ReferenceArrayInput>
    <ReferenceArrayInput source="title_ids" reference="titles" label="Titles">
      <AutocompleteArrayInput optionText="name" />
    </ReferenceArrayInput>
    <ReferenceArrayInput source="vehicle_ids" reference="vehicles" label="Mounts">
      <AutocompleteArrayInput optionText="name" />
    </ReferenceArrayInput>
    <TextInput source="notes" multiline fullWidth />
    <BooleanInput source="active" />
  </SimpleForm>
)

export const CharacterList = () => (
  <List filters={characterFilters} perPage={25} sort={{ field: 'name', order: 'ASC' }}>
    <Datagrid bulkActionButtons={false} rowClick="show">
      <TextField source="name" />
      <TextField source="faction" />
      <TextField source="server" />
      <ReferenceField source="origin_story_id" reference="origin-stories" label="Origin" />
      <NumberField source="level" />
      <ReferenceArrayField source="class_name_ids" reference="class-names" label="Classes">
        <SingleFieldList linkType={false}>
          <ChipField source="name" />
        </SingleFieldList>
      </ReferenceArrayField>
      <ReferenceArrayField source="role_ids" reference="roles" label="Roles">
        <SingleFieldList linkType={false}>
          <ChipField source="name" />
        </SingleFieldList>
      </ReferenceArrayField>
      <BooleanField source="active" />
      <CharacterRowActions />
    </Datagrid>
    <CharacterCards />
  </List>
)

export const CharacterShow = () => (
  <Show actions={<CharacterListActions />}>
    <SimpleShowLayout>
      <TextField source="display_name" label="Display Name" />
      <TextField source="name" />
      <TextField source="faction" />
      <TextField source="server" />
      <ReferenceField source="origin_story_id" reference="origin-stories" label="Origin Story" />
      <NumberField source="level" />
      <NumberField source="valor_rank" label="Valor Rank" />
      <TextField source="race" />
      <TextField source="gender" />
      <TextField source="guild" />
      <TextField source="alignment" />
      <ReferenceArrayField source="class_name_ids" reference="class-names" label="Classes">
        <SingleFieldList linkType={false}>
          <ChipField source="name" />
        </SingleFieldList>
      </ReferenceArrayField>
      <ReferenceArrayField source="role_ids" reference="roles" label="Roles">
        <SingleFieldList linkType={false}>
          <ChipField source="name" />
        </SingleFieldList>
      </ReferenceArrayField>
      <ReferenceArrayField source="title_ids" reference="titles" label="Titles">
        <SingleFieldList linkType={false}>
          <ChipField source="name" />
        </SingleFieldList>
      </ReferenceArrayField>
      <ReferenceArrayField source="vehicle_ids" reference="vehicles" label="Mounts">
        <SingleFieldList linkType={false}>
          <ChipField source="name" />
        </SingleFieldList>
      </ReferenceArrayField>
      <FunctionField source="notes" render={(record) => record.notes || '-'} />
      <NumberField source="crew_skills_count" label="Crew Skills" />
      <NumberField source="titles" />
      <NumberField source="mounts" />
      <BooleanField source="active" />
    </SimpleShowLayout>
  </Show>
)

export const CharacterCreate = () => (
  <Create>
    <CharacterForm />
  </Create>
)

export const CharacterEdit = () => (
  <Edit>
    <CharacterForm />
  </Edit>
)
