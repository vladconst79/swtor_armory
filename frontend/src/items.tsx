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
  NumberField,
  NumberInput,
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
  type RaRecord,
} from 'react-admin'

const rarityChoices = [
  { id: 'common', name: 'Common' },
  { id: 'uncommon', name: 'Uncommon' },
  { id: 'rare', name: 'Rare' },
  { id: 'epic', name: 'Epic' },
  { id: 'legendary', name: 'Legendary' },
]

const bindingChoices = [
  { id: 'none', name: 'None' },
  { id: 'bind_on_pickup', name: 'Bind on Pickup' },
  { id: 'bind_on_equip', name: 'Bind on Equip' },
  { id: 'bind_on_legacy', name: 'Bind on Legacy' },
]

const cargoHoldChoices = [
  { id: 'cargo_hold', name: 'Personal Cargo Hold' },
  { id: 'cargo_hold_shared', name: 'Legacy Cargo Hold' },
  { id: 'cargo_hold_guild', name: 'Guild Cargo Hold' },
]

const itemFilters = [
  <SearchInput key="q" source="q" alwaysOn />,
  <BooleanInput key="mine" source="mine" label="My items" />,
  <SelectInput key="rarity" source="rarity" choices={rarityChoices} />,
  <SelectInput key="binding" source="binding" choices={bindingChoices} />,
  <SelectInput key="cargo_hold" source="cargo_hold" label="Cargo Hold" choices={cargoHoldChoices} />,
  <ReferenceArrayInput key="character_ids" source="character_ids" reference="characters" label="Characters">
    <AutocompleteArrayInput optionText="name" />
  </ReferenceArrayInput>,
]

const ItemRowActions = ({ record }: { record?: RaRecord }) => (
  <>
    <ShowButton record={record} />
    <EditButton record={record} />
    <DeleteButton record={record} mutationMode="pessimistic" />
  </>
)

const ItemForm = () => (
  <SimpleForm>
    <TextInput source="name" validate={[required()]} fullWidth />
    <SelectInput source="rarity" choices={rarityChoices} defaultValue="common" validate={[required()]} />
    <SelectInput source="binding" choices={bindingChoices} defaultValue="none" validate={[required()]} />
    <BooleanInput source="bound" />
    <SelectInput
      source="cargo_hold"
      label="Cargo Hold"
      choices={cargoHoldChoices}
      defaultValue="cargo_hold"
      validate={[required()]}
    />
    <NumberInput source="cargo_bay" label="Cargo Bay" min={1} max={8} defaultValue={1} validate={[required()]} />
    <ReferenceArrayInput source="character_ids" reference="characters" label="Characters">
      <AutocompleteArrayInput optionText="name" />
    </ReferenceArrayInput>
    <BooleanInput source="active" />
  </SimpleForm>
)

export const ItemList = () => (
  <List filters={itemFilters} perPage={25} sort={{ field: 'name', order: 'ASC' }}>
    <Datagrid bulkActionButtons={false} rowClick="show">
      <TextField source="name" />
      <TextField source="rarity" />
      <TextField source="binding" />
      <BooleanField source="bound" />
      <TextField source="cargo_hold" label="Cargo Hold" />
      <NumberField source="cargo_bay" label="Bay" />
      <ReferenceArrayField source="character_ids" reference="characters" label="Characters">
        <SingleFieldList linkType={false}>
          <ChipField source="name" />
        </SingleFieldList>
      </ReferenceArrayField>
      <BooleanField source="active" />
      <ItemRowActions />
    </Datagrid>
  </List>
)

export const ItemShow = () => (
  <Show>
    <SimpleShowLayout>
      <TextField source="name" />
      <TextField source="rarity" />
      <TextField source="binding" />
      <BooleanField source="bound" />
      <TextField source="cargo_hold" label="Cargo Hold" />
      <NumberField source="cargo_bay" label="Cargo Bay" />
      <ReferenceArrayField source="character_ids" reference="characters" label="Characters">
        <SingleFieldList linkType={false}>
          <ChipField source="name" />
        </SingleFieldList>
      </ReferenceArrayField>
      <BooleanField source="active" />
    </SimpleShowLayout>
  </Show>
)

export const ItemCreate = () => (
  <Create>
    <ItemForm />
  </Create>
)

export const ItemEdit = () => (
  <Edit>
    <ItemForm />
  </Edit>
)
