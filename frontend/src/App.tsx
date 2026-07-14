import { Admin, Resource } from 'react-admin'
import './App.css'
import { authProvider } from './authProvider'
import { CharacterCreate, CharacterEdit, CharacterList, CharacterShow } from './characters'
import {
  CharacterCrewSkillCreate,
  CharacterCrewSkillEdit,
  CharacterCrewSkillList,
  CharacterCrewSkillShow,
} from './characterCrewSkills'
import { CrewSkillCreate, CrewSkillEdit, CrewSkillList, CrewSkillShow } from './crewSkills'
import { dataProvider } from './dataProvider'
import { ItemCreate, ItemEdit, ItemList, ItemShow } from './items'
import { LoadoutCreate, LoadoutEdit, LoadoutList, LoadoutShow } from './loadouts'
import {
  OperationCreate,
  OperationEdit,
  OperationList,
  OperationLockoutCreate,
  OperationLockoutEdit,
  OperationLockoutList,
  OperationLockoutShow,
  OperationShow,
} from './operations'
import {
  ClassNameCreate,
  ClassNameEdit,
  ClassNameList,
  ClassNameShow,
  GuildCreate,
  GuildEdit,
  GuildList,
  GuildShow,
  OriginStoryCreate,
  OriginStoryEdit,
  OriginStoryList,
  OriginStoryShow,
  RoleCreate,
  RoleEdit,
  RoleList,
  RoleShow,
  SpecCreate,
  SpecEdit,
  SpecList,
  SpecShow,
  TitleCreate,
  TitleEdit,
  TitleList,
  TitleShow,
  VehicleCreate,
  VehicleEdit,
  VehicleList,
  VehicleShow,
} from './referenceAdmin'
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
  if (resource.name === 'loadouts') {
    return {
      list: LoadoutList,
      show: LoadoutShow,
      create: LoadoutCreate,
      edit: LoadoutEdit,
    }
  }
  if (resource.name === 'items') {
    return {
      list: ItemList,
      show: ItemShow,
      create: ItemCreate,
      edit: ItemEdit,
    }
  }
  if (resource.name === 'crew-skills') {
    return {
      list: CrewSkillList,
      show: CrewSkillShow,
      create: CrewSkillCreate,
      edit: CrewSkillEdit,
    }
  }
  if (resource.name === 'character-crew-skill-relations') {
    return {
      list: CharacterCrewSkillList,
      show: CharacterCrewSkillShow,
      create: CharacterCrewSkillCreate,
      edit: CharacterCrewSkillEdit,
    }
  }
  if (resource.name === 'operations') {
    return {
      list: OperationList,
      show: OperationShow,
      create: OperationCreate,
      edit: OperationEdit,
    }
  }
  if (resource.name === 'operation-lockouts') {
    return {
      list: OperationLockoutList,
      show: OperationLockoutShow,
      create: OperationLockoutCreate,
      edit: OperationLockoutEdit,
    }
  }
  if (resource.name === 'class-names') {
    return {
      list: ClassNameList,
      show: ClassNameShow,
      create: ClassNameCreate,
      edit: ClassNameEdit,
    }
  }
  if (resource.name === 'guilds') {
    return {
      list: GuildList,
      show: GuildShow,
      create: GuildCreate,
      edit: GuildEdit,
    }
  }
  if (resource.name === 'origin-stories') {
    return {
      list: OriginStoryList,
      show: OriginStoryShow,
      create: OriginStoryCreate,
      edit: OriginStoryEdit,
    }
  }
  if (resource.name === 'roles') {
    return {
      list: RoleList,
      show: RoleShow,
      create: RoleCreate,
      edit: RoleEdit,
    }
  }
  if (resource.name === 'specs') {
    return {
      list: SpecList,
      show: SpecShow,
      create: SpecCreate,
      edit: SpecEdit,
    }
  }
  if (resource.name === 'titles') {
    return {
      list: TitleList,
      show: TitleShow,
      create: TitleCreate,
      edit: TitleEdit,
    }
  }
  if (resource.name === 'vehicles') {
    return {
      list: VehicleList,
      show: VehicleShow,
      create: VehicleCreate,
      edit: VehicleEdit,
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
