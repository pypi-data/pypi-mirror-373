# 需在linux环境下运行，依懒pyenv、python==3.13.2、crontab
from crontab import CronTab

def set(name, new_schedule, new_command):
    cron = CronTab(user=True)
    comment ="# "+name 
    for job in cron:
        if comment in job.command:
            # 修改时间表达式和命令
            job.set_command(new_command+comment)
            job.setall(new_schedule)
            cron.write()
            print("任务更新成功")
            return
    # 创建任务
    job = cron.new(command=new_command+comment)
    job.setall(new_schedule)
    cron.write()
    print("任务添加成功")