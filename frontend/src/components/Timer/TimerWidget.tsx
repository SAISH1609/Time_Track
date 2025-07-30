'use client'

import React, { useState, useEffect } from 'react'
import { Play, Pause, Square, RotateCcw } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { useTimer } from '@/hooks/useTimer'

interface TimerWidgetProps {
  currentTask?: {
    id: number
    title: string
    color?: string
  }
  onTaskChange?: (taskId: number) => void
}

export function TimerWidget({ currentTask, onTaskChange }: TimerWidgetProps) {
  const {
    isRunning,
    elapsedTime,
    startTimer,
    pauseTimer,
    stopTimer,
    resetTimer
  } = useTimer()

  const [displayTime, setDisplayTime] = useState('00:00:00')

  useEffect(() => {
    const formatTime = (seconds: number) => {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = seconds % 60
      
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }

    setDisplayTime(formatTime(elapsedTime))
  }, [elapsedTime])

  const handleStart = async () => {
    if (!currentTask) {
      // Show task selection modal or default to a task
      return
    }
    
    try {
      await startTimer(currentTask.id, '')
    } catch (error) {
      console.error('Failed to start timer:', error)
    }
  }

  const handlePause = async () => {
    try {
      await pauseTimer()
    } catch (error) {
      console.error('Failed to pause timer:', error)
    }
  }

  const handleStop = async () => {
    try {
      await stopTimer('')
    } catch (error) {
      console.error('Failed to stop timer:', error)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border">
      <div className="text-center mb-6">
        <div className="text-4xl font-mono font-bold text-gray-900 mb-2">
          {displayTime}
        </div>
        
        {currentTask && (
          <div className="flex items-center justify-center gap-2 mb-4">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: currentTask.color || '#3B82F6' }}
            />
            <span className="text-sm text-gray-600 truncate max-w-48">
              {currentTask.title}
            </span>
          </div>
        )}
        
        {!currentTask && (
          <div className="text-sm text-gray-500 mb-4">
            Select a task to start tracking
          </div>
        )}
      </div>

      <div className="flex justify-center gap-3">
        {!isRunning ? (
          <Button
            onClick={handleStart}
            disabled={!currentTask}
            variant="primary"
            size="lg"
            className="flex items-center gap-2"
          >
            <Play className="w-4 h-4" />
            Start
          </Button>
        ) : (
          <Button
            onClick={handlePause}
            variant="secondary"
            size="lg"
            className="flex items-center gap-2"
          >
            <Pause className="w-4 h-4" />
            Pause
          </Button>
        )}

        <Button
          onClick={handleStop}
          disabled={!isRunning}
          variant="outline"
          size="lg"
          className="flex items-center gap-2"
        >
          <Square className="w-4 h-4" />
          Stop
        </Button>

        <Button
          onClick={resetTimer}
          variant="ghost"
          size="lg"
          className="flex items-center gap-2"
        >
          <RotateCcw className="w-4 h-4" />
          Reset
        </Button>
      </div>

      {isRunning && (
        <div className="mt-4 text-center">
          <div className="inline-flex items-center gap-2 text-sm text-green-600">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            Timer running
          </div>
        </div>
      )}
    </div>
  )
}
