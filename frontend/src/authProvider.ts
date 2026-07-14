import type { AuthProvider } from 'react-admin'
import { apiUrl, authTokenStorageKey, userStorageKey } from './config'

type LoginParams = {
  username: string
  password: string
}

type CurrentUser = {
  id: number
  username: string
  is_active: boolean
  is_swtor_admin: boolean
}

const getToken = () => localStorage.getItem(authTokenStorageKey)

export const getAuthHeaders = (): HeadersInit => {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const fetchCurrentUser = async (): Promise<CurrentUser> => {
  const response = await fetch(`${apiUrl}/auth/me`, {
    headers: getAuthHeaders(),
  })

  if (!response.ok) {
    throw new Error('Authentication required')
  }

  return response.json()
}

export const authProvider: AuthProvider = {
  async login({ username, password }: LoginParams) {
    const response = await fetch(`${apiUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })

    if (!response.ok) {
      throw new Error('Invalid username or password')
    }

    const body = await response.json()
    localStorage.setItem(authTokenStorageKey, body.access_token)

    const user = await fetchCurrentUser()
    localStorage.setItem(userStorageKey, JSON.stringify(user))
  },

  async logout() {
    localStorage.removeItem(authTokenStorageKey)
    localStorage.removeItem(userStorageKey)
  },

  async checkAuth() {
    if (!getToken()) {
      throw new Error('Authentication required')
    }
  },

  async checkError(error) {
    if (error?.status === 401) {
      localStorage.removeItem(authTokenStorageKey)
      localStorage.removeItem(userStorageKey)
      throw new Error('Authentication required')
    }
  },

  async getIdentity() {
    const storedUser = localStorage.getItem(userStorageKey)
    const user: CurrentUser = storedUser ? JSON.parse(storedUser) : await fetchCurrentUser()

    return {
      id: user.id,
      fullName: user.username,
    }
  },

  async getPermissions() {
    const storedUser = localStorage.getItem(userStorageKey)
    const user: CurrentUser = storedUser ? JSON.parse(storedUser) : await fetchCurrentUser()

    return user.is_swtor_admin ? 'admin' : 'user'
  },
}
