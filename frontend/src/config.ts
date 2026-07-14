export const apiUrl =
  import.meta.env.VITE_API_URL?.replace(/\/$/, '') ?? 'http://localhost:8000/api'

export const authTokenStorageKey = 'swtor_armory_token'
export const userStorageKey = 'swtor_armory_user'
