import React, { useState, useEffect, useRef } from 'react';
import { CheckCircle2, Settings, Hourglass, BarChart2 } from 'lucide-react';
import { initialModules } from '../assets/modulesData';

export default function ProcessTracker({ file }) {
  const [modules, setModules] = useState(initialModules);
  const [now, setNow] = useState(Date.now());

  // Ticking effect to calculate visual live elapsed time
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 100);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (start, currentNow) => {
    if (!start) return 'TBD';
    const elapsed = Math.max(0, currentNow - start);
    if (elapsed < 1000) return `${elapsed}ms`;
    return `${(elapsed / 1000).toFixed(1)}s`;
  };

  useEffect(() => {
    let intervalId;

    const startPipelineAndPoll = async () => {
      if (file) {
        const formData = new FormData();
        formData.append("file", file);
        try {
          await fetch("http://localhost:8000/start", {
            method: "POST",
            body: formData,
          });
        } catch (error) {
          console.error("Error starting pipeline:", error);
        }
      }

      intervalId = setInterval(async () => {
        try {
          const res = await fetch("http://localhost:8000/progress");
          if (res.ok) {
            const data = await res.json();
            if (data && Object.keys(data).length > 0) {
              console.log("📩 Polled DATA:", data);

              if (data.status) {
                setModules((prev) =>
                  prev.map((m) => {
                    if (m.id === data.id) {
                      
                      const isNewlyActive = m.status !== 'RUNNING_ACTIVE' && data.status === 'in_progress';
                      const isNewlyCompleted = m.status !== 'COMPLETED' && data.status === 'completed';

                      let newStartTime = m.startTime;
                      if (isNewlyActive && !m.startTime) {
                        newStartTime = Date.now();
                      }

                      let newTimeValue = m.timeValue;
                      let newTimeLabel = m.timeLabel;
                      if (isNewlyCompleted) {
                        newTimeValue = formatTime(newStartTime || Date.now(), Date.now());
                        newTimeLabel = "TOTAL TIME";
                      } else if (data.status === 'in_progress') {
                        newTimeLabel = "ELAPSED";
                      }

                      return {
                        ...m,
                        status: data.status === 'completed' ? 'COMPLETED' : 'RUNNING_ACTIVE',
                        progress: data.progress !== undefined ? data.progress : m.progress,
                        message: data.message || m.message,
                        data: data.status === 'completed' ? (data.data || m.data) : m.data,
                        startTime: newStartTime,
                        timeValue: newTimeValue,
                        timeLabel: newTimeLabel
                      };
                    }
                    return m;
                  })
                );
              }

              if (data.status === "completed" || data.status === "stopped" || data.status === "error") {
                console.log("🛑 Polling stopped because status is", data.status);
                clearInterval(intervalId);
              }
            }
          }
        } catch (error) {
          console.error("Polling error:", error);
        }
      }, 500); // Polling every half second 
    };

    startPipelineAndPoll();

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [file]);

  return (
    <div className="flex-1 w-full max-w-6xl mx-auto p-8 z-10">

      {/* Header Section */}
      <div className="flex justify-between items-start mb-10 mt-6">
        <div className="max-w-3xl">
          <h1 className="text-4xl font-bold tracking-tight text-white mb-4">PROCESS TRACKER</h1>
          <p className="text-brand-text-muted text-[15px] leading-relaxed max-w-2xl">
            Real-time modular orchestration of the active pipeline sequence. Monitoring latency, throughput, and execution states.
          </p>
        </div>

        <div className="bg-[#1b1f23] border border-[#2b3036] rounded-sm p-4 flex flex-col justify-center min-w-[240px]">
          <p className="text-[#647182] text-xs font-mono font-bold tracking-widest mb-1">SYSTEM PULSE</p>
          <div className="flex items-center justify-between">
            <span className="text-brand-cyan text-xl font-bold font-mono tracking-wider drop-shadow-[0_0_8px_rgba(0,210,211,0.5)]">
              98.2% NOMINAL
            </span>
            <BarChart2 className="text-brand-cyan opacity-80" size={24} />
          </div>
        </div>
      </div>

      {/* Modules List */}
      <div className="space-y-[6px]">
        {modules.map((mod) => {
          const isCompleted = mod.status === 'COMPLETED';
          const isActive = mod.status === 'RUNNING_ACTIVE';
          const isPending = mod.status === 'PENDING';

          return (
            <div
              key={mod.id}
              className={`flex items-center px-6 py-5 rounded-sm relative border transition-colors ${isActive
                ? 'bg-[#1b2226] border-brand-cyan'
                : 'bg-[#181b1f] border-[#22272c] hover:bg-[#1a1e22]'
                }`}
            >
              {/* Active Left Border Highlight */}
              {isActive && (
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-brand-cyan shadow-[0_0_8px_rgba(0,210,211,0.8)]"></div>
              )}

              {/* Status Icon */}
              <div className="w-12 flex-shrink-0 flex items-center justify-center">
                {isCompleted && <CheckCircle2 className="text-[#647182]" size={22} />}
                {isActive && <Settings className="text-brand-cyan animate-spin-slow drop-shadow-[0_0_8px_rgba(0,210,211,0.6)]" size={22} />}
                {isPending && <Hourglass className="text-[#3a4149]" size={22} />}
              </div>

              {/* Module Name & ID */}
              <div className="w-48 flex-shrink-0 pr-4">
                <p className="text-[#586470] text-[11px] font-mono font-bold tracking-widest mb-1">{mod.id}</p>
                <p className={`text-[15px] font-bold tracking-wide ${isActive ? 'text-brand-cyan drop-shadow-[0_0_4px_rgba(0,210,211,0.4)]' : (isCompleted ? 'text-[#e2e8f0]' : 'text-[#647182]')}`}>
                  {mod.name}
                </p>
              </div>

              {/* Progress Section */}
              <div className="flex-1 px-8 flex flex-col justify-center relative">
                {/* Message placed ABOVE the progress bar line */}
                <div className="flex justify-between items-end mb-1">
                  <span className={`text-[11px] font-mono tracking-wide ${isActive ? 'text-[#8e9ba9]' : 'text-[#586470]'}`}>
                    {mod.message || (isPending ? "Awaiting execution..." : "")}
                  </span>
                  <span className={`text-[12px] font-mono font-bold ${isActive ? 'text-brand-cyan drop-shadow-[0_0_4px_rgba(0,210,211,0.5)]' : (isCompleted ? 'text-[#8e9ba9]' : 'text-[#586470]')}`}>
                    {mod.progress === 100 || mod.progress === 0 ? mod.progress : mod.progress.toFixed(1)}%
                  </span>
                </div>
                
                {/* The Progress Bar Line */}
                <div className="h-1.5 w-full bg-[#101214] overflow-hidden rounded-full border border-[#1e2328]">
                  <div
                    className={`h-full ${isActive ? 'bg-brand-cyan shadow-[0_0_8px_rgba(0,210,211,1)]' : (isCompleted ? 'bg-[#4b5563]' : 'bg-transparent')}`}
                    style={{ width: `${mod.progress}%`, transition: isActive ? 'width 0.5s ease-out' : 'none' }}
                  ></div>
                </div>
                
                {/* Status indicator BELOW the progress line */}
                <div className="flex justify-start mt-1.5">
                   <span className={`text-[9px] font-mono font-bold tracking-widest uppercase ${isActive ? 'text-brand-cyan' : 'text-[#586470]'}`}>
                    STATUS: {mod.status}
                  </span>
                </div>
              </div>

              {/* Timestamp Section */}
              <div className="w-32 flex-shrink-0 text-right pr-6 flex flex-col justify-center">
                <p className="text-[10px] font-mono font-bold tracking-widest text-[#586470] mb-1">{mod.timeLabel}</p>
                <p className={`text-[12px] font-mono ${isCompleted || isActive ? 'text-[#e2e8f0]' : 'text-[#4b5563]'}`}>
                  {isCompleted ? mod.timeValue : (isActive ? formatTime(mod.startTime, now) : 'TBD')}
                </p>
              </div>

              {/* Action Button */}
              <div className="w-32 flex-shrink-0 flex justify-end">
                <button
                  disabled={!isCompleted || Object.keys(mod.data || {}).length === 0}
                  onClick={() => console.log(`Payload for ${mod.name}:`, mod.data)}
                  className={`px-4 py-2 text-[11px] font-bold tracking-widest rounded-sm transition-colors ${
                    isCompleted && Object.keys(mod.data || {}).length > 0
                      ? 'bg-brand-cyan text-[#101214] hover:bg-[#1ae5e6] shadow-[0_0_12px_rgba(0,210,211,0.3)]'
                      : (isActive
                        ? 'bg-transparent border border-[#3a4149] text-[#8e9ba9] hover:bg-[#22272c]'
                        : 'bg-transparent border border-[#2b3036] text-[#3a4149] cursor-not-allowed')
                    }`}
                >
                  VIEW LOGS
                </button>
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
}
