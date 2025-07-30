export interface Task {
  id: number
  title: string
  description?: string
  status: 'todo' | 'in_progress' | 'completed' | 'archived'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  estimated_hours?: number
  project_id?: number
  parent_task_id?: number
  user_id: number
  tags?: string[]
  color: string
  due_date?: string
  is_billable: boolean
  created_at: string
  updated_at?: string
  completed_at?: string
  ace_task_id?: string
  ace_category?: string
  is_active: boolean
}

export interface TaskCreate {
  title: string
  description?: string
  status?: 'todo' | 'in_progress' | 'completed' | 'archived'
  priority?: 'low' | 'medium' | 'high' | 'urgent'
  estimated_hours?: number
  project_id?: number
  parent_task_id?: number
  tags?: string[]
  color?: string
  due_date?: string
  is_billable?: boolean
}

export interface TaskUpdate {
  title?: string
  description?: string
  status?: 'todo' | 'in_progress' | 'completed' | 'archived'
  priority?: 'low' | 'medium' | 'high' | 'urgent'
  estimated_hours?: number
  project_id?: number
  parent_task_id?: number
  tags?: string[]
  color?: string
  due_date?: string
  is_billable?: boolean
  completed_at?: string
}

export interface TaskWithSubTasks extends Task {
  sub_tasks: Task[]
}

export interface TaskSummary {
  id: number
  title: string
  status: string
  priority: string
  color: string
  project_name?: string
  total_time: number
  is_running: boolean
}

export interface QuickTaskCreate {
  title: string
  project_id?: number
}

export interface TaskStatusUpdate {
  status: 'todo' | 'in_progress' | 'completed' | 'archived'
}

export interface TaskTimeInfo {
  task_id: number
  task_title: string
  total_time: number
  entries_count: number
  last_entry?: string
  is_running: boolean
}
