export interface ApiResponse<T = any> {
  data: T
  message?: string
  success: boolean
}

export interface ApiError {
  message: string
  status: number
  code?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface TimerStatus {
  is_running: boolean
  current_entry?: TimeEntry
  elapsed_time: number
}

export interface TimeEntry {
  id: number
  user_id: number
  task_id: number
  project_id?: number
  start_time: string
  end_time?: string
  duration?: number
  description?: string
  notes?: string
  is_billable: boolean
  is_running: boolean
  is_manual: boolean
  created_at: string
  updated_at?: string
  ace_entry_id?: string
  synced_to_ace: boolean
  is_validated: boolean
}

export interface TimeEntryCreate {
  task_id: number
  project_id?: number
  start_time?: string
  end_time?: string
  duration?: number
  description?: string
  notes?: string
  is_billable?: boolean
  is_manual?: boolean
}

export interface TimerStart {
  task_id: number
  description?: string
}

export interface TimerStop {
  description?: string
  notes?: string
}

export interface TimerUpdate {
  description?: string
}
