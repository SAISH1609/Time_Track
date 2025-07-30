'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { api } from '@/lib/api'

interface TimerState {
  isRunning: boolean
  currentEntry: any | null
  elapsedTime: number
}

export function useTimer() {
  const [timerState, setTimerState] = useState<TimerState>({
    isRunning: false,
    currentEntry: null,
    elapsedTime: 0
  })

  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const startTimeRef = useRef<number | null>(null)

  // Fetch timer status on mount
  useEffect(() => {
    fetchTimerStatus()
  }, [])

  // Update elapsed time when timer is running
  useEffect(() => {
    if (timerState.isRunning) {
      intervalRef.current = setInterval(() => {
        if (startTimeRef.current) {
          const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000)
          setTimerState(prev => ({ ...prev, elapsedTime: elapsed }))
        }
      }, 1000)
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [timerState.isRunning])

  const fetchTimerStatus = useCallback(async () => {
    try {
      const response = await api.get('/timer/status')
      const data = response.data

      setTimerState({
        isRunning: data.is_running,
        currentEntry: data.current_entry,
        elapsedTime: data.elapsed_time || 0
      })

      if (data.is_running && data.current_entry) {
        // Calculate start time based on current entry
        const entryStart = new Date(data.current_entry.start_time).getTime()
        startTimeRef.current = Date.now() - (data.elapsed_time * 1000)
      } else {
        startTimeRef.current = null
      }
    } catch (error) {
      console.error('Failed to fetch timer status:', error)
    }
  }, [])

  const startTimer = useCallback(async (taskId: number, description: string = '') => {
    try {
      const response = await api.post('/timer/start', {
        task_id: taskId,
        description
      })

      const entry = response.data
      startTimeRef.current = Date.now()
      
      setTimerState({
        isRunning: true,
        currentEntry: entry,
        elapsedTime: 0
      })

      return entry
    } catch (error) {
      console.error('Failed to start timer:', error)
      throw error
    }
  }, [])

  const pauseTimer = useCallback(async () => {
    try {
      await api.post('/timer/pause')
      
      setTimerState(prev => ({
        ...prev,
        isRunning: false
      }))

      startTimeRef.current = null
    } catch (error) {
      console.error('Failed to pause timer:', error)
      throw error
    }
  }, [])

  const stopTimer = useCallback(async (description: string = '', notes: string = '') => {
    try {
      const response = await api.post('/timer/stop', {
        description,
        notes
      })

      setTimerState({
        isRunning: false,
        currentEntry: null,
        elapsedTime: 0
      })

      startTimeRef.current = null
      return response.data
    } catch (error) {
      console.error('Failed to stop timer:', error)
      throw error
    }
  }, [])

  const updateTimer = useCallback(async (description: string) => {
    try {
      const response = await api.put('/timer/update', {
        description
      })

      setTimerState(prev => ({
        ...prev,
        currentEntry: response.data
      }))

      return response.data
    } catch (error) {
      console.error('Failed to update timer:', error)
      throw error
    }
  }, [])

  const switchTask = useCallback(async (taskId: number, description: string = '') => {
    try {
      const response = await api.post(`/timer/switch/${taskId}`, null, {
        params: { description }
      })

      const entry = response.data
      startTimeRef.current = Date.now()
      
      setTimerState({
        isRunning: true,
        currentEntry: entry,
        elapsedTime: 0
      })

      return entry
    } catch (error) {
      console.error('Failed to switch task:', error)
      throw error
    }
  }, [])

  const resetTimer = useCallback(() => {
    setTimerState({
      isRunning: false,
      currentEntry: null,
      elapsedTime: 0
    })
    startTimeRef.current = null
  }, [])

  const getTimerStats = useCallback(async () => {
    try {
      const response = await api.get('/timer/stats')
      return response.data
    } catch (error) {
      console.error('Failed to get timer stats:', error)
      throw error
    }
  }, [])

  return {
    isRunning: timerState.isRunning,
    currentEntry: timerState.currentEntry,
    elapsedTime: timerState.elapsedTime,
    startTimer,
    pauseTimer,
    stopTimer,
    updateTimer,
    switchTask,
    resetTimer,
    fetchTimerStatus,
    getTimerStats
  }
}
