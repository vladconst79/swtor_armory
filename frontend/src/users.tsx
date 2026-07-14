import {
  BooleanField,
  BooleanInput,
  Create,
  Datagrid,
  DateField,
  Edit,
  EditButton,
  List,
  PasswordInput,
  SearchInput,
  Show,
  ShowButton,
  SimpleForm,
  SimpleShowLayout,
  TextField,
  TextInput,
  required,
  usePermissions,
  type RaRecord,
} from 'react-admin'

const userFilters = [
  <SearchInput key="q" source="q" alwaysOn />,
  <BooleanInput key="is_active" source="is_active" label="Active" />,
  <BooleanInput key="is_swtor_admin" source="is_swtor_admin" label="SWTOR Admin" />,
]

const UserRowActions = ({ record }: { record?: RaRecord }) => {
  const { permissions } = usePermissions()
  const writable = permissions === 'admin'

  return (
    <>
      <ShowButton record={record} />
      {writable ? <EditButton record={record} /> : null}
    </>
  )
}

const UserForm = ({ creating = false }: { creating?: boolean }) => (
  <SimpleForm sanitizeEmptyValues>
    <TextInput source="username" validate={[required()]} fullWidth />
    <PasswordInput
      source="password"
      label={creating ? 'Temporary Password' : 'Reset Password'}
      helperText={creating ? undefined : 'Leave blank to keep the current password.'}
      validate={creating ? [required()] : undefined}
      fullWidth
    />
    <BooleanInput source="is_active" label="Active" />
    <BooleanInput source="is_swtor_admin" label="SWTOR Admin" />
  </SimpleForm>
)

export const UserList = () => (
  <List filters={userFilters} perPage={25} sort={{ field: 'username', order: 'ASC' }}>
    <Datagrid bulkActionButtons={false} rowClick="show">
      <TextField source="id" />
      <TextField source="username" />
      <BooleanField source="is_active" label="Active" />
      <BooleanField source="is_swtor_admin" label="SWTOR Admin" />
      <DateField source="created_at" label="Created" showTime />
      <DateField source="updated_at" label="Updated" showTime />
      <UserRowActions />
    </Datagrid>
  </List>
)

export const UserShow = () => (
  <Show>
    <SimpleShowLayout>
      <TextField source="id" />
      <TextField source="username" />
      <BooleanField source="is_active" label="Active" />
      <BooleanField source="is_swtor_admin" label="SWTOR Admin" />
      <DateField source="created_at" label="Created" showTime />
      <DateField source="updated_at" label="Updated" showTime />
    </SimpleShowLayout>
  </Show>
)

export const UserCreate = () => (
  <Create>
    <UserForm creating />
  </Create>
)

export const UserEdit = () => (
  <Edit>
    <UserForm />
  </Edit>
)
