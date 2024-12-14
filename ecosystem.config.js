module.exports = {
    apps: [
      {
        name: "urv5-tasks",            // 任务名称
        script: "python3",             // 使用 Python 执行脚本
        args: "gradio_task.py",        // 执行的 Python 脚本
        cron_restart: "*/5 * * * *",   // 每 5 分钟执行一次
        autorestart: true,             // 启用自动重启
        watch: false,                  // 禁止文件变化时自动重启
        max_memory_restart: "1G",      // 超过 1GB 内存时重启脚本
      }
    ]
  };
  