import { Admin, Resource } from 'react-admin'
import './App.css'
import { authProvider } from './authProvider'
import { CharacterCreate, CharacterEdit, CharacterList, CharacterShow } from './characters'
import { dataProvider } from './dataProvider'
import { ResourceCreate, ResourceEdit, ResourceList, ResourceShow } from './resources'
import { resources, type ResourceDefinition } from './resourceConfig'

const theme = {
  palette: {
    mode: 'dark' as const,
    primary: {
      main: '#d6b35a',
    },
    secondary: {
      main: '#7fb6d9',
    },
    background: {
      default: '#10141a',
      paper: '#171d25',
    },
  },
  shape: {
    borderRadius: 6,
  },
  typography: {
    fontFamily:
      'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  },
}

const Dashboard = () => (
  <section className="dashboard">
    <div>
      <p className="eyebrow">SWTOR Armory</p>
      <h1>Legacy command center</h1>
      <p>
        Manage characters and account-wide reference data from one admin shell.
      </p>
    </div>
    <dl>
      <div>
        <dt>Characters</dt>
        <dd>Roster and ownership-scoped records</dd>
      </div>
      <div>
        <dt>Reference data</dt>
        <dd>Admin-managed game catalogs</dd>
      </div>
      <div>
        <dt>Security</dt>
        <dd>Backend permissions remain authoritative</dd>
      </div>
    </dl>
  </section>
)

const listFor = (resource: ResourceDefinition) => () => <ResourceList resource={resource} />
const showFor = (resource: ResourceDefinition) => () => <ResourceShow resource={resource} />
const createFor = (resource: ResourceDefinition) => () => <ResourceCreate resource={resource} />
const editFor = (resource: ResourceDefinition) => () => <ResourceEdit resource={resource} />

const resourceComponents = (resource: ResourceDefinition) => {
  if (resource.name === 'characters') {
    return {
      list: CharacterList,
      show: CharacterShow,
      create: CharacterCreate,
      edit: CharacterEdit,
    }
  }

  return {
    list: listFor(resource),
    show: showFor(resource),
    create: createFor(resource),
    edit: editFor(resource),
  }
}

function App() {
  return (
    <Admin
      title="SWTOR Armory"
      dataProvider={dataProvider}
      authProvider={authProvider}
      dashboard={Dashboard}
      theme={theme}
      requireAuth
    >
      {resources.map((resource) => {
        const components = resourceComponents(resource)
        return (
          <Resource
            key={resource.name}
            name={resource.name}
            options={{ label: resource.label }}
            list={components.list}
            show={components.show}
            create={components.create}
            edit={components.edit}
          />
        )
      })}
    </Admin>
  )
}

export default App
