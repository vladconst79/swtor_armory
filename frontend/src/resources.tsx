import {
  BooleanField,
  BooleanInput,
  Create,
  CreateButton,
  Datagrid,
  DateField,
  DateInput,
  DeleteButton,
  Edit,
  EditButton,
  List,
  NumberField,
  NumberInput,
  required,
  Show,
  ShowButton,
  SimpleForm,
  SimpleShowLayout,
  TextField,
  TextInput,
  TopToolbar,
  usePermissions,
  type RaRecord,
} from 'react-admin'
import type { ReactNode } from 'react'
import type { ResourceDefinition, ResourceField } from './resourceConfig'

const isAdmin = (permissions: unknown) => permissions === 'admin'

const canWrite = (resource: ResourceDefinition, permissions: unknown) =>
  !resource.adminManaged || isAdmin(permissions)

const ResourceListActions = ({ resource }: { resource: ResourceDefinition }) => {
  const { permissions } = usePermissions()

  return <TopToolbar>{canWrite(resource, permissions) ? <CreateButton /> : null}</TopToolbar>
}

const RowActions = ({ resource, record }: { resource: ResourceDefinition; record?: RaRecord }) => {
  const { permissions } = usePermissions()
  const writable = canWrite(resource, permissions)

  return (
    <>
      <ShowButton record={record} />
      {writable ? <EditButton record={record} /> : null}
      {writable ? <DeleteButton record={record} mutationMode="pessimistic" /> : null}
    </>
  )
}

const renderField = (field: ResourceField) => {
  if (field.kind === 'boolean') {
    return <BooleanField key={field.source} source={field.source} label={field.label} />
  }
  if (field.kind === 'date') {
    return <DateField key={field.source} source={field.source} label={field.label} />
  }
  if (field.kind === 'number') {
    return <NumberField key={field.source} source={field.source} label={field.label} />
  }
  return <TextField key={field.source} source={field.source} label={field.label} />
}

const renderInput = (field: ResourceField) => {
  if (field.readOnly) {
    return null
  }

  const validate = field.required ? [required()] : undefined
  if (field.kind === 'boolean') {
    return <BooleanInput key={field.source} source={field.source} label={field.label} />
  }
  if (field.kind === 'date') {
    return <DateInput key={field.source} source={field.source} label={field.label} validate={validate} />
  }
  if (field.kind === 'number') {
    return <NumberInput key={field.source} source={field.source} label={field.label} validate={validate} />
  }
  return <TextInput key={field.source} source={field.source} label={field.label} validate={validate} />
}

const GuardedForm = ({
  children,
  resource,
}: {
  children: ReactNode
  resource: ResourceDefinition
}) => {
  const { permissions, isPending } = usePermissions()

  if (isPending) {
    return null
  }

  if (!canWrite(resource, permissions)) {
    return <div className="permission-note">Admin privileges are required for this action.</div>
  }

  return children
}

export const ResourceList = ({ resource }: { resource: ResourceDefinition }) => (
  <List
    actions={<ResourceListActions resource={resource} />}
    perPage={25}
    sort={{ field: resource.fields[1]?.source ?? 'id', order: 'ASC' }}
  >
    <Datagrid bulkActionButtons={false} rowClick="show">
      {resource.fields.map(renderField)}
      <RowActions resource={resource} />
    </Datagrid>
  </List>
)

export const ResourceShow = ({ resource }: { resource: ResourceDefinition }) => (
  <Show>
    <SimpleShowLayout>{resource.fields.map(renderField)}</SimpleShowLayout>
  </Show>
)

export const ResourceCreate = ({ resource }: { resource: ResourceDefinition }) => (
  <GuardedForm resource={resource}>
    <Create>
      <SimpleForm>{resource.fields.map(renderInput)}</SimpleForm>
    </Create>
  </GuardedForm>
)

export const ResourceEdit = ({ resource }: { resource: ResourceDefinition }) => (
  <GuardedForm resource={resource}>
    <Edit>
      <SimpleForm>{resource.fields.map(renderInput)}</SimpleForm>
    </Edit>
  </GuardedForm>
)
