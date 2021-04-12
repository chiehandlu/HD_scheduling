#!/usr/bin/env python
# coding: utf-8

# Step 1: Import the cp_model
from __future__ import print_function
from ortools.sat.python import cp_model

# Step 3: Declare the linear solver, or MIP, or cp_model
model = cp_model.CpModel()

# Step 4: Create a database and requests
num_employees = 4
employees_name = ['Dr 徐', 'Dr 謝', 'Dr 胡', 'Dr 杰'] 
m = int(input("要輸入幾月班表: "))
months = [32, 29, 32, 31, 32, 31, 32, 32, 31, 32, 31, 32]
num_days = months[m-1] 
# - -> off, M -> Morning, A -> Afternoon, I -> Morning + Afternoon
shifts = ['-', 'M', 'A', 'C']
costs = [0, 3, 1, 4]
work_time = [0, 1, 1, 2]

num_shifts = len(shifts)

all_employees = range(num_employees)
all_days = range(num_days)
all_shifts = range(num_shifts)


### 一號是禮拜幾
x = int(input("月初1號是禮拜幾（禮拜天是0,禮拜一是1）: "))
print()


### 輸入值班時間
# 值班時間盡量可以排班，像是上面request (employee, shift, day, weight)
# 盡量要(M or A) & C ＝> 不要 O => 只要修改"值班日期(d)"就好
real_duty_time = []

for i in range(num_employees):
    real_duty = input(employees_name[i]+" 幾號值班(每一天用“,”格開)：")
    if real_duty == '':
        pass
    else:
        real_duty = list(map(int, real_duty.split(',')))
        for d in real_duty:
            real_duty_time_list = (i, 0, d, 2)
            real_duty_time.append(real_duty_time_list)

            
duty_time = []
for a, b, c, d in real_duty_time:
    # 在c後面 ＋ s 表示 “月初距離禮拜一幾天” 再 - 1 天
    # ex. 109/9/1是禮拜二，所以 + 1 - 1 = 0
    add_day_of_duty = (a, b, c - 1, d)
    duty_time.append(add_day_of_duty)
    
# 值班隔天早上盡量off -> duty隔天“盡量”不要選'M'
duty_next_morning = []
for a, b, c, d in duty_time:
    nextday_of_duty = (a, 1, c+1, d)
    duty_next_morning.append(nextday_of_duty)
    
# 值班隔天下午盡量off(寧願早上看，也不要下午看) -> duty隔天“盡量”不要選'A' or 'C'
duty_next_afternoon = []
for a, b, c, d in duty_time:
    nextday_of_duty_1 = (a, 2, c+1, d+5)
    duty_next_afternoon.append(nextday_of_duty_1)
    nextday_of_duty_2 = (a, 3, c+1, d+5)
    duty_next_afternoon.append(nextday_of_duty_2)
    
print()


# 加上休假時間固定設為off，類似上面fixed_assignment (employee, shift, day)用法
real_off_day = []

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
            
print()



off_day = []
for a, b, c in real_off_day:
    true_real_off_day = (a, b, c-1)
    off_day.append(true_real_off_day)



real_requests = []

# 腎超(2)sono
hsu_sono_day = input("Dr徐幾號早上做超音波：")
if hsu_sono_day == '':
    pass
else:
    hsu_sono_day = list(map(int, hsu_sono_day.split(',')))
    morning = [1, 3]
    for m in morning:
        for d in hsu_sono_day:
            hsu_sono_day_real = [0, m, d, 2]
            real_requests.append(hsu_sono_day_real)
            
hu_sono_day = input("Dr胡幾號下午做超音波：")
if hu_sono_day == '':
    pass
else:
    hu_sono_day = list(map(int, hu_sono_day.split(',')))
    for a in range(2,4):
        for d in hu_sono_day:
            hu_sono_day_real = [2, a, d, 2]
            real_requests.append(hu_sono_day_real)   

print()


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


# IDS 日期
chieh_IDS_day = input("Dr杰幾號早上去IDS：")
if chieh_IDS_day == '':
    pass
else:
    chieh_IDS_day = list(map(int, chieh_IDS_day.split(',')))
    morning = [1, 3]
    for a in morning:
        for d in chieh_IDS_day:
            chieh_IDS_day_real = [3, a, d, 10]
            real_requests.append(chieh_IDS_day_real)
            
print()


requests = []
for a, b, c, d in real_requests:
    true_requests = (a, b, c-1, d)
    requests.append(true_requests)



# 禮拜一
monday = []
for i in range(num_days):
    if ((i%7) + x -1)% 7 == 1:
        monday.append(i)
        for i in monday:
            if i == 0:
                monday.remove(i)        

# 禮拜二
tuesday = []
for i in range(num_days):
    if ((i%7) + x -1)% 7 == 2:
        tuesday.append(i)
        for i in tuesday:
            if i == 0:
                tuesday.remove(i)
# 禮拜三
wednesday = []
for i in range(num_days):
    if ((i%7) + x -1)% 7 == 3:
        wednesday.append(i)
        for i in wednesday:
            if i == 0:
                wednesday.remove(i)
# 禮拜四
thursday = []
for i in range(num_days):
    if ((i%7) + x -1)% 7 == 4:
        thursday.append(i)
        for i in thursday:
            if i == 0:
                thursday.remove(i)
# 禮拜五
friday = []
for i in range(num_days):
    if ((i%7) + x -1)% 7 == 5:
        friday.append(i)
        for i in friday:
            if i == 0:
                friday.remove(i)
# 禮拜六
saturday = []
for i in range(num_days):
    if ((i%7) + x -1)% 7 == 6:
        saturday.append(i)
        for i in saturday:
            if i == 0:
                saturday.remove(i)
        
week = [monday, tuesday, wednesday, thursday, friday, saturday]



# 禮拜天時間固定設為off，類似上面fixed_assignment (employee, shift, day)用法
fixed_assignments = []
true_sunday = []
for i in range(num_days):
    if ((i%7) + x -1)% 7 == 0:
        true_sunday.append(i)
        for i in true_sunday:
            if i == 0:
                true_sunday.remove(i)
        
for i in range(num_employees):
    for j in true_sunday:
            sunday = [i, 0, j-1]
            fixed_assignments.append(sunday)



non_sunday = []
for i in range(num_days):
    if ((i%7) + x -1)% 7 != 0:
        non_sunday.append(i)
        for i in non_sunday:
            if i == 0:
                non_sunday.remove(i)            



# 加上OPD時間盡量off，像是上面request (employee, shift, day, weight) 不要(M or A) & C 
# 早上OPD的人, M & C 盡量不要排
# 徐, 謝, 胡, 杰 禮拜幾早上OPD
morning_in_week = [3, 3, 0, 1]
morning = [1, 3]
real_opd_requests = []
for i in range(num_employees):
    real_OPD_day = week[morning_in_week[i]]
    for k in morning:
        for j in real_OPD_day:
            opd_time = (i, k, j, 2)
            real_opd_requests.append(opd_time)

# 下午OPD的人, A & C 盡量不要排
# 徐, 謝, 胡, 杰 禮拜幾下午OPD            
afternoon_in_week = [0, 1, 4, 2]
afternoon = [2, 3]
for i in range(num_employees):
    real_OPD_day = week[afternoon_in_week[i]]
    for j in real_OPD_day:
        for k in afternoon:
            opd_time = (i, k, j, 2)
            real_opd_requests.append(opd_time)

 # Dr謝 禮拜幾早上上課不要排，M & C 盡量不要排，像是上面request (employee, shift, day, weight)
y = input("Dr謝禮拜幾固定不排: ")
z = input("禮拜"+ y + "早上or下午不排(早上->1, 下午->2): ")

if y == '':
    pass
else:
    if z == '':
        pass
    elif int(z) == 1:
        other_requests = week[int(y)-1]
        for k in morning:
            for j in other_requests:
                other_time = (1, k, j, 10)
                real_opd_requests.append(other_time)
    elif int(z) == 2:
        other_requests = week[int(y)-1]
        for k in afternoon:
            for j in other_requests:
                other_time = (1, k, j, 10)
                real_opd_requests.append(other_time)


opd_time = []
for a, b, c, d in real_opd_requests:
    # 在c後面 ＋ s 表示 “月初距離禮拜一幾天” 再 - 1 天
    # ex. 109/9/1是禮拜二，所以 + 1 - 1 = 0
    add_day_of_opd = (a, b, c - 1, d)
    opd_time.append(add_day_of_opd)
    
print()



# 解釋報告，先輸入哪兩天解釋報告，類似上面fixed_assignment (employee, shift, day)用法
explain_day = input("哪兩天解釋報告：")
if explain_day == '':
    pass
else:
    explain_day = list(map(int, explain_day.split(',')))
    for e in explain_day:
        print()
        for i in range(num_employees):
            explain_shift = input(employees_name[i]+" "+str(e)+" 號上什麼班'off->0', 'M->1', 'A->2', 'C->3'：")
            if explain_shift == '':
                pass
            else:
                real_explain_day = [i, int(explain_shift), e-1]
                fixed_assignments.append(real_explain_day) 
                
print()



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



# Step 6: Define the constraints
# 1) 每人每天只能在其中一班工作
for e in range(num_employees):
    for d in range(num_days):
        model.Add(sum(work[e, s, d] for s in range(num_shifts)) == 1)
        
# 2) 除了禮拜天，每天每個人的shifts*costs加起來分數要等於8 (O = 0, M = 3, A = 1, C = 4)        
for i in non_sunday:
    works = [work[e, s, i-1] * costs[s] for s in range(1, num_shifts) for e in range(num_employees)] 
    model.Add(sum(works) == 8)
        
# 3) 除了禮拜天，每天的 “M” or “A” 數目要小於3個
for i in non_sunday:
    for s in range(1, num_shifts):
        model.Add(sum(work[e, s, i-1] for e in range(num_employees)) <= 2)
            
# 4) 每個禮拜六要是兩個C
for d in saturday:
    model.Add(sum(work[e, 3, d-1] for e in range(num_employees)) == 2)
    
# 5) Fixed assignments. 讓e,s,d跟Fixed assignments內tuple一樣的，都為1
# 這樣就會讓所有有用到Fixed assignments指定的做
for e, s, d in fixed_assignments:
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
min_shifts_per_employee = ((len(non_sunday) * 4) // num_employees) - 4
# 每天有4班，一週有7天，，但禮拜天固定不用上，所以總班數=num_weeks * 6 * 4
max_shifts_per_employee = min_shifts_per_employee + 4

for e in range(num_employees):
    num_shifts_per_employee = 0
    for d in non_sunday:
        for h in range(1, num_shifts):
            num_shifts_per_employee += work[e, h, d] * work_time[h]
            
    model.Add(num_shifts_per_employee <= max_shifts_per_employee)
    model.Add(num_shifts_per_employee >= min_shifts_per_employee)



# Step 7: Define the objective
model.Minimize(
    sum(obj_bool_vars[i] * obj_bool_coeffs[i] for i in range(len(obj_bool_vars)))
    + sum(obj_bool_opd_vars[i] * obj_bool_opd_coeffs[i] for i in range(len(obj_bool_opd_vars))))



# Step 8: Create a solver and invoke solve
solver = cp_model.CpSolver()

solution_printer = cp_model.ObjectiveSolutionPrinter()
status = solver.SolveWithSolutionCallback(model, solution_printer)



# Step 9: Call a printer and display the results
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print('worker 0(徐), worker 1(謝), worker 2(胡), worker 3(杰)')
    print()
    different_header = [['S ', 'M ', 'T ', 'W ', 'T ', 'F ', 'S '], 
                        ['M ', 'T ', 'W ', 'T ', 'F ', 'S ', 'S '], 
                        ['T ', 'W ', 'T ', 'F ', 'S ', 'S ', 'M '], 
                        ['W ', 'T ', 'F ', 'S ', 'S ', 'M ', 'T '], 
                        ['T ', 'F ', 'S ', 'S ', 'M ', 'T ', 'W '],
                        ['F ', 'S ', 'S ', 'M ', 'T ', 'W ', 'T '], 
                        ['S ', 'S ', 'M ', 'T ', 'W ', 'T ', 'F ']]
    header = '          '
    for i in range(num_days-1):
        if i <=6:
            header += different_header[x][i]
        else:
            j = i % 7
            header += different_header[x][j]
    print(header)
    
    for e in range(num_employees):
        schedule = ''
        for d in range(num_days-1):
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
print(solver.ResponseStats())

