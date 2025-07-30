export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at?: string
  last_login?: string
  avatar_url?: string
  timezone: string
  default_project_id?: number
}

export interface UserCreate {
  email: string
  username: string
  password: string
  full_name?: string
}

export interface UserLogin {
  username: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
  expires_in: number
}

export interface UserProfile {
  id: number
  email: string
  username: string
  full_name?: string
  avatar_url?: string
  timezone: string
  created_at: string
  last_login?: string
}

export interface UserSettings {
  timezone?: string
  default_project_id?: number
  notification_preferences?: Record<string, any>
  ace_integration_settings?: Record<string, any>
}
