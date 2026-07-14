import type {
  CreateParams,
  DataProvider,
  DeleteParams,
  GetListParams,
  GetManyParams,
  GetManyReferenceParams,
  GetOneParams,
  Identifier,
  RaRecord,
  UpdateParams,
} from 'react-admin'
import { getAuthHeaders } from './authProvider'
import { apiUrl } from './config'

type ApiListResponse<RecordType extends RaRecord = RaRecord> = {
  data: RecordType[]
  total: number
}

type ApiErrorBody = {
  detail?: string
}

class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

const buildHeaders = (headers?: HeadersInit): HeadersInit => ({
  'Content-Type': 'application/json',
  ...getAuthHeaders(),
  ...headers,
})

const request = async <Result>(path: string, options: RequestInit = {}): Promise<Result> => {
  const response = await fetch(`${apiUrl}/${path}`, {
    ...options,
    headers: buildHeaders(options.headers),
  })

  if (!response.ok) {
    let message = response.statusText
    try {
      const body: ApiErrorBody = await response.json()
      message = body.detail ?? message
    } catch {
      // Keep the HTTP status text when the response has no JSON body.
    }
    throw new ApiError(message, response.status)
  }

  if (response.status === 204) {
    return undefined as Result
  }

  return response.json()
}

const listQuery = ({ pagination, sort, filter }: GetListParams): string => {
  const query = new URLSearchParams()
  query.set('page', String(pagination?.page ?? 1))
  query.set('per_page', String(pagination?.perPage ?? 25))
  query.set('sort', sort?.field ?? 'id')
  query.set('order', (sort?.order ?? 'ASC').toLowerCase())
  query.set('filter', JSON.stringify(filter ?? {}))
  return query.toString()
}

const getManyFilter = (ids: Identifier[]): string => {
  const query = new URLSearchParams()
  query.set('page', '1')
  query.set('per_page', String(Math.max(ids.length, 1)))
  query.set('filter', JSON.stringify({ id: ids }))
  return query.toString()
}

const withoutId = <RecordType extends RaRecord>(data: Partial<RecordType>) => {
  const payload = { ...data }
  delete payload.id
  return payload
}

export const dataProvider: DataProvider = {
  async getList<RecordType extends RaRecord = RaRecord>(resource: string, params: GetListParams) {
    return request<ApiListResponse<RecordType>>(`${resource}?${listQuery(params)}`)
  },

  async getOne<RecordType extends RaRecord = RaRecord>(resource: string, params: GetOneParams) {
    const data = await request<RecordType>(`${resource}/${params.id}`)
    return { data }
  },

  async getMany<RecordType extends RaRecord = RaRecord>(resource: string, params: GetManyParams) {
    const response = await request<ApiListResponse<RecordType>>(`${resource}?${getManyFilter(params.ids)}`)
    return { data: response.data }
  },

  async getManyReference<RecordType extends RaRecord = RaRecord>(
    resource: string,
    params: GetManyReferenceParams,
  ) {
    const filter = { ...params.filter, [params.target]: params.id }
    return this.getList<RecordType>(resource, { ...params, filter })
  },

  async create<RecordType extends Omit<RaRecord, 'id'> = RaRecord>(
    resource: string,
    params: CreateParams,
  ) {
    const data = await request<RecordType & { id: Identifier }>(resource, {
      method: 'POST',
      body: JSON.stringify(withoutId(params.data)),
    })
    return { data }
  },

  async update<RecordType extends RaRecord = RaRecord>(resource: string, params: UpdateParams) {
    const data = await request<RecordType>(`${resource}/${params.id}`, {
      method: 'PATCH',
      body: JSON.stringify(withoutId(params.data)),
    })
    return { data }
  },

  async updateMany(resource: string, params) {
    await Promise.all(
      params.ids.map((id: Identifier) =>
        request(`${resource}/${id}`, {
          method: 'PATCH',
          body: JSON.stringify(withoutId(params.data)),
        }),
      ),
    )
    return { data: params.ids }
  },

  async delete<RecordType extends RaRecord = RaRecord>(resource: string, params: DeleteParams<RecordType>) {
    await request<void>(`${resource}/${params.id}`, { method: 'DELETE' })
    return { data: params.previousData ?? ({ id: params.id } as RecordType) }
  },

  async deleteMany(resource: string, params) {
    await Promise.all(params.ids.map((id: Identifier) => request<void>(`${resource}/${id}`, { method: 'DELETE' })))
    return { data: params.ids }
  },
}
