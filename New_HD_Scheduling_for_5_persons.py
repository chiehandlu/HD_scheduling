#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Step 1: Import the cp_model
from __future__ import print_function
from ortools.sat.python import cp_model

# Step 3: Declare the linear solver, or MIP, or cp_model
model = cp_model.CpModel()

# Step 4: Create a database and requests
num_employees = 5
employees_name = [
    'Dr 陳', 'Dr 謝', 'Dr 徐', 'Dr 胡', 'Dr 杰'] #杰暫時改成陳主任（０號）位置去排
num_weeks = 5
num_days = num_weeks * 7

# - -> off, M -> Morning, A -> Afternoon, I -> Morning + Afternoon
shifts = ['-', 'M', 'A', 'C']
costs = [0, 3, 1, 4]
work_time = [0, 1, 1, 2]

num_shifts = len(shifts)

all_employees = range(num_employees)
all_days = range(num_days)
all_shifts = range(num_shifts)


# In[2]:


### 輸入上個月最後班表

# Fixed assignment: (employee, shift, day).
# This fixes the first 2 days of the schedule.
# 將每個月最後幾天到第一個禮拜之前的舊班表填入 ex. 填入109/8/31號當禮拜一之後再排５週
fixed_assignments = [
#     # Day 1
#     (0, 0, 0), (1, 1, 0), (2, 3, 0), (3, 0, 0), (4, 2, 0),
#     Day 2
#     (0, 0, 1), (1, 1, 1), (2, 2, 1), (3, 0, 1), (4, 3, 1), 
#     Day 3
#    (0, 0, 2), (1, 2, 2), (2, 1, 2), (3, 0, 2), (4, 3, 2), 
#     Day 4    
#    (0, 0, 3), (1, 2, 3), (2, 3, 3), (3, 0, 3), (4, 1, 3), 
#     Day 5
#     (0, 2, 4), (1, 0, 4), (2, 3, 4), (3, 1, 4), (4, 0, 4), 
#     Day 6
#     (0, 0, 5), (1, 0, 5), (2, 0, 5), (3, 3, 5), (4, 3, 5) 
]


# In[3]:


### 輸入值班時間

# 值班時間盡量可以排班，像是上面request (employee, shift, day, weight)
# 盡量要(M or A) & C ＝> 不要 O => 只要修改"值班日期(d)"就好
real_duty_time = [
    # Dr.陳 值班時間
    (0, 0, 9, 2), 
    # Dr.謝 值班時間
    (1, 0, 5, 2), (1, 0, 17, 2), (1, 0, 22, 2), 
    # Dr.徐 值班時間
    (2, 0, 13, 2), (2, 0, 20, 2), (2, 0, 25, 2),
    # Dr.胡 值班時間
    (3, 0, 2, 2), (3, 0, 8, 2), (3, 0, 23, 2),
    # Dr.杰 值班時間
    (4, 0, 1, 2), (4, 0, 13, 2), (4, 0, 26, 2),
]


# In[4]:


### 月初距離禮拜一幾天
s = int(input("月初距離禮拜一幾天: "))

duty_time = []
for a, b, c, d in real_duty_time:
    # 在c後面 ＋ s 表示 “月初距離禮拜一幾天” 再 - 1 天
    # ex. 109/9/1是禮拜二，所以 + 1 - 1 = 0
    add_day_of_duty = (a, b, c + s - 1, d)
    duty_time.append(add_day_of_duty)
    
# 值班隔天早上盡量off -> duty隔天“盡量”不要選'M'
duty_next_morning = []
for a, b, c, d in duty_time:
    nextday_of_duty = (a, 2, c+1, d)
    duty_next_morning.append(nextday_of_duty)
    
# 值班隔天下午盡量off(寧願早上看，也不要下午看) -> duty隔天“盡量”不要選'A' or 'C'
duty_next_afternoon = []
for a, b, c, d in duty_time:
    nextday_of_duty_1 = (a, 2, c+1, d+5)
    duty_next_afternoon.append(nextday_of_duty_1)
    nextday_of_duty_2 = (a, 3, c+1, d+5)
    duty_next_afternoon.append(nextday_of_duty_2)


# In[5]:


# 加上休假時間固定設為off，類似上面fixed_assignment (employee, shift, day)用法
real_off_day = [
    # 輸入其他休假時間
    # (4, 0, 21)
]


# In[17]:


for i in range(num_employees):
    start_time = input(employees_name[i]+" 從幾號休：")
    if start_time == '':
        pass
    else:
        real_start = int(start_time)
        real_end = int(input(employees_name[i]+" 休到幾號："))
        for d in range(real_start, real_end+1):
            off_time = [i, 0, d]
            real_off_day.append(off_time)


# In[7]:


off_day = []
for a, b, c in real_off_day:
    true_real_off_day = (a, b, c+s-1)
    off_day.append(true_real_off_day)


# In[8]:


### 輸入其他要求，像是腎超(2)、大武(2)、屏監(2)、PD門診(2) => 將有事的時間("M" or "A") and "C"之weight設為正，這樣就會盡量避開

# Request: (employee, shift, day, weight)
# 負的weight表示employee要求要上這班，正的表示要求不要上這班.
real_requests = []

# 腎超(2)sono
    #(3, 2, 2, 2), (3, 2, 9, 2), #(3, 2, 30, 2),
    #(3, 3, 2, 2), (3, 3, 9, 2), #(3, 3, 30, 2),
hsu_sono_day = input("Dr徐幾號早上做超音波：")
if hsu_sono_day == '':
    pass
else:
    hsu_sono_day = list(map(int, hsu_sono_day.split(',')))
    morning = [1, 3]
    for m in morning:
        for d in hsu_sono_day:
            hsu_sono_day_real = [2, m, d, 2]
            real_requests.append(hsu_sono_day_real)
            
hu_sono_day = input("Dr胡幾號下午做超音波：")
if hu_sono_day == '':
    pass
else:
    hu_sono_day = list(map(int, hu_sono_day.split(',')))
    for a in range(2,4):
        for d in hu_sono_day:
            hu_sono_day_real = [3, a, d, 2]
            real_requests.append(hu_sono_day_real) 

# 大武(2)dawu
for i in range(num_employees):
    dawu_all_day = input(employees_name[i]+" 幾號\"整天\"在大武(每一天用“,”格開)：")
    if dawu_all_day == '':
        pass
    else:
        dawu_all_day = list(map(int, dawu_all_day.split(',')))
        for d in dawu_all_day:
            dawu_all_day_real = [i, 0, d, -2]
            real_requests.append(dawu_all_day_real)
    
    dawu_morning = input(employees_name[i]+" 幾號\"早上\"在大武(每一天用“,”格開)：")
    if dawu_morning == '':
        pass
    else:
        dawu_morning = list(map(int, dawu_morning.split(',')))
        morning = [1, 3]
        for m in morning:
            for d in dawu_morning:
                dawu_morning_real = [i, m, d, 2]
                real_requests.append(dawu_morning_real)
            
    dawu_afternoon = input(employees_name[i]+" 幾號\"下午\"在大武(每一天用“,”格開)：")
    if dawu_afternoon == '':
        pass
    else:
        dawu_afternoon = list(map(int, dawu_afternoon.split(',')))
        for a in range(2,4):
            for d in dawu_afternoon:
                dawu_afternoon_real = [i, a, d, 2]
                real_requests.append(dawu_afternoon_real)
    print()

requests = []
for a, b, c, d in real_requests:
    true_requests = (a, b, c+s-1, d)
    requests.append(true_requests)
print(requests)


# In[9]:


# 加上OPD時間盡量off，像是上面request (employee, shift, day, weight)
# 不要(M or A) & C

opd_time = [
    # Dr.陳 固定禮拜三下午、禮拜五上午OPD
    #(0, 2, 2, 2), (0, 2, 9, 2), (0, 2, 16, 2), (0, 2, 23, 2), (0, 2, 30, 2),
    #(0, 3, 2, 2), (0, 3, 9, 2), (0, 3, 16, 2), (0, 3, 23, 2), (0, 3, 30, 2),
    (0, 1, 4, 2), (0, 1, 11, 2), (0, 1, 18, 2), (0, 1, 25, 2), (0, 1, 32, 2),
    (0, 3, 4, 2), (0, 3, 11, 2), (0, 3, 18, 2), (0, 3, 25, 2), (0, 3, 32, 2),
    # Dr.謝 固定禮拜二下午、禮拜四上午OPD
    (1, 2, 1, 2), (1, 2, 8, 2), (1, 2, 15, 2), (1, 2, 22, 2), (1, 2, 29, 2),
    (1, 3, 1, 2), (1, 3, 8, 2), (1, 3, 15, 2), (1, 3, 22, 2), (1, 3, 29, 2),
    (1, 1, 3, 2), (1, 1, 10, 2), (1, 1, 17, 2), (1, 1, 24, 2), (1, 1, 31, 2),
    (1, 3, 3, 2), (1, 3, 10, 2), (1, 3, 17, 2), (1, 3, 24, 2), (1, 3, 31, 2),
    # Dr.謝 固定禮拜一、下午禮拜四上午、禮拜三上午上課
    #(1, 2, 0, 2), (1, 2, 7, 2), (1, 2, 14, 2), (1, 2, 21, 2), (1, 2, 28, 2),
    #(1, 3, 0, 2), (1, 3, 7, 2), (1, 3, 14, 2), (1, 3, 21, 2), (1, 3, 28, 2),
    #(1, 1, 3, 2), (1, 1, 10, 2), (1, 1, 17, 2), (1, 1, 24, 2), (1, 1, 31, 2),
    #(1, 3, 3, 2), (1, 3, 10, 2), (1, 3, 17, 2), (1, 3, 24, 2), (1, 3, 31, 2),
    (1, 1, 2, 2), (1, 1, 9, 2), (1, 1, 16, 2), (1, 1, 23, 2), (1, 1, 30, 2),
    (1, 3, 2, 2), (1, 3, 9, 2), (1, 3, 16, 2), (1, 3, 23, 2), (1, 3, 30, 2),
    # Dr.徐 固定禮拜一下午、禮拜四上午OPD
    (2, 2, 0, 2), (2, 2, 7, 2), (2, 2, 14, 2), (2, 2, 21, 2), (2, 2, 28, 2),
    (2, 3, 0, 2), (2, 3, 7, 2), (2, 3, 14, 2), (2, 3, 21, 2), (2, 3, 28, 2),
    (2, 1, 3, 2), (2, 1, 10, 2), (2, 1, 17, 2), (2, 1, 24, 2), (2, 1, 31, 2),
    (2, 3, 3, 2), (2, 3, 10, 2), (2, 3, 17, 2), (2, 3, 24, 2), (2, 3, 31, 2),
    # Dr.胡 固定禮拜一上午、禮拜五下午OPD
    (3, 1, 0, 2), (3, 1, 7, 2), (3, 1, 14, 2), (3, 1, 21, 2), (3, 1, 28, 2),
    (3, 3, 0, 2), (3, 3, 7, 2), (3, 3, 14, 2), (3, 3, 21, 2), (3, 3, 28, 2),
    (3, 2, 4, 2), (3, 2, 11, 2), (3, 2, 18, 2), (3, 2, 25, 2), (3, 2, 32, 2),
    (3, 3, 4, 2), (3, 3, 11, 2), (3, 3, 18, 2), (3, 3, 25, 2), (3, 3, 32, 2),
    # Dr.杰 固定禮拜二上午、禮拜三下午OPD、禮拜三上午IDS
    (4, 1, 1, 2), (4, 1, 8, 2), (4, 1, 15, 2), (4, 1, 22, 2), (4, 1, 29, 2),
    (4, 3, 1, 2), (4, 3, 8, 2), (4, 3, 15, 2), (4, 3, 22, 2), (4, 3, 29, 2),
    (4, 2, 1, 2), (4, 1, 9, 2), (4, 1, 16, 2), (4, 1, 23, 2), (4, 1, 30, 2),
    (4, 2, 2, 2), (4, 2, 9, 2), (4, 2, 16, 2), (4, 2, 23, 2), (4, 2, 30, 2), 
    (4, 3, 2, 2), (4, 3, 9, 2), (4, 3, 16, 2), (4, 3, 23, 2), (4, 3, 30, 2), 
]

# 加上禮拜天時間固定設為off，類似上面fixed_assignment (employee, shift, day)用法
sunday = [
    (0, 0, 6), (0, 0, 13), (0, 0, 20), (0, 0, 27), (0, 0, 34),  # Dr.陳 固定禮拜天上午Off
    (1, 0, 6), (1, 0, 13), (1, 0, 20), (1, 0, 27), (1, 0, 34),  # Dr.謝 固定禮拜天上午Off
    (2, 0, 6), (2, 0, 13), (2, 0, 20), (2, 0, 27), (2, 0, 34),  # Dr.徐 固定禮拜天上午Off
    (3, 0, 6), (3, 0, 13), (3, 0, 20), (3, 0, 27), (3, 0, 34),  # Dr.胡 固定禮拜天上午Off
    (4, 0, 6), (4, 0, 13), (4, 0, 20), (4, 0, 27), (4, 0, 34),  # Dr.杰 固定禮拜天上午Off
]


# In[10]:


# 解釋報告，類似上面fixed_assignment (employee, shift, day)用法
real_explain_day = [
    # 輸入解釋報告時間
    #(0, 1, 25), (0, 1, 26), 
    (1, 2, 22), 
    (2, 1, 22), (2, 1, 23), 
    (3, 2, 22), (3, 3, 23), 
    (4, 1, 22), (4, 2, 23),
]

explain_day = []
for a, b, c in real_explain_day:
    true_explain_day = (a, b, c+s-1)
    explain_day.append(true_explain_day)
print(explain_day)


# In[11]:


# Step 5: Create the variables
work = {}
for e in range(num_employees):
    for s in range(num_shifts):
        for d in range(num_days):
            work[e, s, d] = model.NewBoolVar('work%i_%i_%i' % (e, s, d))
            
# Linear terms of the objective in a minimization context.
obj_bool_vars = []
obj_bool_coeffs = []
obj_bool_opd_vars = []
obj_bool_opd_coeffs = []


# In[12]:


# Step 6: Define the constraints
# 1) 每人每天只能在其中一班工作
for e in range(num_employees):
    for d in range(num_days):
        model.Add(sum(work[e, s, d] for s in range(num_shifts)) == 1)
        
# 2) 除了禮拜天，每天每個人的shifts*costs加起來分數要等於4 (O = 0, M = 1, A = 1, C = 2)
for w in range(num_weeks):
    for d in range(6):
        works = [work[e, s, w * 7 + d] * costs[s] for s in range(1, num_shifts) for e in range(num_employees)] 
        model.Add(sum(works) == 8)
        
# 3) 除了禮拜天，每天的 “M” or “A” 數目要小於3個
for w in range(num_weeks):
    for d in range(6):
        for s in range(1, num_shifts):
            model.Add(sum(work[e, s, w * 7 + d] for e in range(num_employees)) <= 2)
            
# 4) 每個禮拜六要是兩個C
Day_Saturday = [5, 12, 19, 26, 33]

for d in Day_Saturday:
    model.Add(sum(work[e, 3, d] for e in range(num_employees)) == 2)
    
# 5) Fixed assignments. 讓e,s,d跟Fixed assignments內tuple一樣的，都為1
# 這樣就會照指定的前兩天做
for e, s, d in fixed_assignments:
    model.Add(work[e, s, d] == 1)

# 5) 解釋報告，讓e,s,d跟Fixed assignments內tuple一樣的，都為1
# 這樣就會照指定的前兩天做
for e, s, d in explain_day:
    model.Add(work[e, s, d] == 1)
    
# 6) 禮拜天每個人都off
for e, s, d in sunday:
    model.Add(work[e, s, d] == 1)
    
# 7) 值班時間盡量要上班、值班隔天盡量不要上班
for e, s, d, w in duty_time:
    obj_bool_vars.append(work[e, s, d])
    obj_bool_coeffs.append(w)    

for e, s, d, w in duty_next_morning:
    obj_bool_vars.append(work[e, s, d])
    obj_bool_coeffs.append(w)
    
for e, s, d, w in duty_next_afternoon:
    obj_bool_vars.append(work[e, s, d])
    obj_bool_coeffs.append(w)
    
# 8) 休假絕對off
for e, s, d in off_day:
    model.Add(work[e, s, d] == 1)
    
# 9) 盡量符合每個人的request
# Employee requests讓e,s,d,w跟requests裡面一樣的形成obj_bool_vars(e,s,d)和obj_bool_coeffs(w)
# 因為要求想上的weight是負數，要求不想上的是正數，所以之後objective要求minimize的數值
# 因為work[e, s, d]是BoolVar，所以objective用Bool_Vars
for e, s, d, w in requests:
    obj_bool_vars.append(work[e, s, d])
    obj_bool_coeffs.append(w)
    
# 10) OPD時間固定，最好不要排 ＝ -2 分
for e, s, d, w in opd_time:
    obj_bool_opd_vars.append(work[e, s, d])
    obj_bool_opd_coeffs.append(w)
    
# 11) 顯示每個人每個月最多上幾班，最少上幾班
min_shifts_per_employee = ((num_weeks * 6 * 4) // num_employees) - 3
# 每天有4班，一週有7天，，但禮拜天固定不用上，所以總班數=num_weeks * 6 * 4
max_shifts_per_employee = min_shifts_per_employee + 3

for e in range(num_employees):
    num_shifts_per_employee = 0
    for d in range(num_weeks * 7):
        for s in range(1, num_shifts):
            num_shifts_per_employee += work[e, s, d] * work_time[s]
            
    model.Add(num_shifts_per_employee <= max_shifts_per_employee)
    model.Add(num_shifts_per_employee >= min_shifts_per_employee)


# In[13]:


# Step 7: Define the objective
model.Minimize(
    sum(obj_bool_vars[i] * obj_bool_coeffs[i] for i in range(len(obj_bool_vars)))
    + sum(obj_bool_opd_vars[i] * obj_bool_opd_coeffs[i] for i in range(len(obj_bool_opd_vars))))


# In[14]:


# Step 8: Create a solver and invoke solve
solver = cp_model.CpSolver()

solution_printer = cp_model.ObjectiveSolutionPrinter()
status = solver.SolveWithSolutionCallback(model, solution_printer)


# In[15]:


# Step 9: Call a printer and display the results
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print('worker 0(陳), worker 1(謝), worker 2(徐), worker 3(胡), worker 4(杰)')
    print()
    header = '          '
    for w in range(num_weeks):
        header += 'M T W T F S S '
    print(header)
    for e in range(num_employees):
        schedule = ''
        for d in range(num_days):
            for s in range(num_shifts):
                if solver.BooleanValue(work[e, s, d]):
                    schedule += shifts[s] + ' '
        print('worker %i: %s' % (e, schedule))
    print()
    for e in range(num_employees):
        assigned = 0
        for d in range(num_days):
            if solver.Value(work[(e, 1, d)]) == 1:
                assigned += 1
            elif solver.Value(work[(e, 2, d)]) == 1:
                assigned += 1
            elif solver.Value(work[(e, 3, d)]) == 1:
                assigned += 2
        print('worker %i assigned to %s works' % (e, assigned))
        
    print()
    print('Penalties:')
    for i, var in enumerate(obj_bool_vars):
        if solver.BooleanValue(var):
            penalty = obj_bool_coeffs[i]
            if penalty > 0:
                print('  %s violated, penalty=%i' % (var.Name(), penalty))
            else:
                print('  %s fulfilled, gain=%i' % (var.Name(), -penalty))

#     for i, var in enumerate(obj_int_vars):
#         if solver.Value(var) > 0:
#             print('  %s violated by %i, linear penalty=%i' %
#                   (var.Name(), solver.Value(var), obj_int_coeffs[i]))
            
            
print()
print(solver.ResponseStats())


# In[ ]:





# In[ ]:





# 
