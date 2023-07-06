import numpy as np
import scipy as sp
import pandas as pd
import math
import Visualise as Vis
import random2 as rnd
import time
import datetime
import pyopencl as cl


def scal(v):  # Lenth of the vector
    return np.linalg.norm(v, ord=2)


def v(v1):  # vector
    return np.array(v1)


def unvec(v):  # unit vector
    uv = v / scal(v)
    return uv


def dist(v1, v2):  # distance between vectors
    return scal(v1 - v2)


def v12(v1, v2):
    return v1 - v2


def ranvec(r):  # Random vector with lengh r
    rv = v([rnd.uniform(-r, r), 2 * (rnd.getrandbits(1) - 0.5) * (r ** 2 - rnd.uniform(-r, r) ** 2) ** 0.5])
    return rv


def ranrv(r):  # Случайный радиус-вектор длинны r
    a = rnd.uniform(0, 2 * math.pi)
    rr = rnd.uniform(0, r)
    rv = v([rr * math.cos(a), rr * math.sin(a)])  # в радианах
    return rv


def vsum(v_list):
    return sum(v_list)  # Sum of N-diemensional vectors


def rotvec(vec, al):
    # rotates 2D vector on AL degrees, multiplies rotation matrix on vector   v' = M*v
    rotation_mx = v([[math.cos(math.radians(al)), math.sin(math.radians(al))],
                     [-1 * math.sin(math.radians(al)), math.cos(math.radians(al))]])
    return np.matmul(vec, rotation_mx)


def format_table(system):
    lines = []
    for line in system.to_numpy():
        lines.append(
            [str(line[1]).replace(' ', ''), line[2], v([line[3], line[4]]), v([line[5], line[6]]),
             line[7].replace(' ', ''),
             line[8]])
    # print(*lines, sep='\n')
    return lines


# numerical methods


eiler = lambda x_nm, y_n, h: x_nm + h * y_n
adams = lambda x_nm, y_n, y_nd, h: x_nm + h * 3 / 2 * y_n - h / 2 * y_nd
# force functions
f_ij = lambda ri, rj, mi, mj: v(((rj - ri) * mi * mj * G) / (
    scal(ri - rj)) ** 3)  # функция силы Ньютоновской гравитации, действующей между двумя телами, даны массы и положения
analytic_f = lambda r0, v0, t: [(r0 + v0 * t - 5 * t ** 2), (v0 - r * t)]  # EXAMPLE!
# def analytic_f(r0, v0, t):  # EXAMPLE!
#     rt = r0 + v0*t - 5 * t**2
#     vt = v0 - r*t
#     return [rt, vt]

# CONSTANTS
G = 0.0001184069  # 09138


# ДОБАВИТЬ КОНСТАНТЫ ДЛЯ ПЕРЕВОДА? ПОДКЛЮЧИТЬ СИ ТАБЛИЦУ И ПЕРЕВОДИТЬ

def simul(method, objects, dir, end, dt, delta_cur, inum, pulse_table, field, dir_n):
    simulation_time = time.time()

    # def u_ob(coor, obj, n): #coor - vector, obj1 - Star, потенциал, создаваемый телом obj1 в точке coor / на шаге n
    #     if dist(coor, obj.r[n]) == 0:
    #         return 0
    #     else:
    #         u = -1*G*obj.m / dist(coor, obj.r[n])
    #         return u
    # #print(u)
    # def U(coor, system, n): #потенциал, создаваемый всеми в точке coor /на шаге n
    #     us = []
    #     for obj in system:
    #         us.append(u_ob(coor, obj, n))
    #     U = sum(us)
    #     #print(U)
    #     return U
    # def U_matrix(system, n):
    #     matrix = []
    #     y = -5
    #     while y <= 5:
    #         U_line = []
    #         x = -5
    #         while x <= 5:
    #             coor = [x, y]
    #             U_line.append(U(coor, system, n))
    #             x += 0.05
    #         y += 0.05
    #         matrix.append(U_line)
    #     # print(matrix)
    #     return matrix
    # Functions for potential net

    def f12(obj1, obj2, n):  # Force between first and second given objects on time step n. Uses lambda f_ij
        return f_ij(obj1.r[n - 1], obj2.r[n - 1], obj1.m, obj2.m)

    def f(obj, system, n):  # Sum of forces affected on given object in system on time step n. Uses lambda f_ij
        obj.fn = []
        for other in system:
            if obj != other:
                obj.fn.append(f12(obj, other, n))
        return vsum(obj.fn)
        obj.fn.clear()

    enn = int(end / dt)
    dt = dir * dt

    class Object:
        # Has two underclasses, each real object from table can be initialised as one of them, or as both.
        def __init__(self, m, r0, v0, system, colour, start_angle, *args, **kwargs):
            self.colour = colour
            self.start_angle = start_angle
            self.m = m
            self.r0 = v(r0)
            self.v0 = v(v0)
            self.r = []
            self.v = []
            self.f = []
            self.t = []

            self.r.append(rotvec(r0, start_angle))
            self.v.append(rotvec(v0, start_angle))
            self.t.append(0)
            self.f.append(f(self, system, 1))

            # FOR ADAMS
            self.r.append(v(self.r[0] + dt * self.v[0]))
            self.v.append(v(self.v[0] + dt * self.f[0] / self.m))
            self.t.append(1)
            self.f.append(f(self, system, 2))

            if pulse_table == True:
                self.Ps = []
                self.Ps.append(v(self.v[0] * self.m))
                self.Ps.append(v(self.v[1] * self.m))

        def print_object(self):
            print("id=" + str(self.i), self.m, "f" + str(self.f), "v" + str(self.v), "r" + str(self.r),
                  "t" + str(self.t))

        def print_object_coor(self):
            print("id=" + str(self.i), self.r)

        def makeXY(self):
            # devider = 1
            # devider = int(devider)
            x_s0 = []
            y_s0 = []
            for i in self.r:
                x_s0.append(i[0])
                y_s0.append(i[1])
                # x_s0 = x_s0[::devider]
                # y_s0 = y_s0[::devider]
            return [x_s0, y_s0]

        def reper(self, n):
            self.r[n] = self.r[n] - system[0].r[n]

    class DynamicObject(Object):
        def iteration(self, system, n, dt):
            # Objects which trajectory deternined by others with force
            def eiler_method(fs, vs, rs, m):
                vs.append(eiler(vs[n - 1], (fs[n - 1] / m), dt))
                rs.append(eiler(rs[n - 1], vs[n], dt))

            def midpoint_method(fs, vs, rs, ms):
                vs.append(v(vs[n - 1] + dt * f(rs[n - 1] + dt / 2 * f(rs[n - 1])) / m))  # Midpoint
                rs.append(v(rs[n - 1] + dt / 2 * (vs[n - 1] + vs[n - 2])))

            def adams_method(fs, vs, rs, m):
                vs.append(adams(vs[n - 1], (fs[n - 1] / m), (fs[n - 2] / m), dt))
                rs.append(adams(rs[n - 1], (vs[n - 1] / m), (vs[n - 2] / m), dt))
                # vs.append(v(vs[n - 1] + dt / 2 * (3 * fs[n] / m - fs[n - 1] / m)))
                # rs.append(v(rs[n - 1] + dt / 2 * (3 * vs[n] - vs[n - 1])))

            self.t.append(self.t[n - 1] + dt)
            self.f.append(f(self, system, n))

            eiler_method(self.f, self.v, self.r, self.m)
            # midpoint_method(self.f, self.v, self.r, self.m)

            if pulse_table == True:
                self.Ps.append(v(self.v[n] * self.m))

    class AnalyticObject(Object):
        # Object, on which others don't affect, which is going on it's own independent trajectory
        # But others feel it's force
        def iteration(self, n, dt):
            self.t.append(self.t[n - 1] + dt)
            self.v.append(analytic_f(self.r0, self.v0, (n * dt))[1])
            self.r.append(analytic_f(self.r0, self.v0, (n * dt))[0])

    system = []
    for ob in objects:
        # system.append(object( ob[1], ob[2]+ranrv(delta_cur), ob[3], ob[4], system, ob[6].replace("'", '') ))
        system.append(DynamicObject(ob[1], ob[2] + ranrv(delta_cur), ob[3], system, ob[4].replace("'", ''), ob[5]))

    if field == True:
        inum = 'f'
        delta_cur = 0
        Vis.vis_field(U_matrix(system, 0), system, inum, delta_cur, dir_n)  # 0 is case of n

    # --define function for pulse---
    if pulse_table == True:
        def Pn(system, n):
            ps = []
            for ob in system:
                ps.append(ob.Ps[n - 1])
            return scal(vsum(ps))

    # ---Iterator---
    for n in range(2, enn):
        # dtn = dt #FOR DYNAMIC TIME STEP!!!
        # Star.iter(galaxy, n, dt)
        for ss in system:
            ss.iteration(system, n, dt)
            ss.reper(n)
            # ss.print_object() #вывести всё про точку

    # ---PULSE TABLE---
    if pulse_table == True:
        PS = []  # Добавляем в список значения полного импульса с итераций
        for n in range(0, enn):
            PS.append(Pn(galaxy, n))
        tP = pd.DataFrame(
            {
                "t": galaxy[0].t,
                "P": PS
            })
        tP.to_csv('tP.csv')
        print(PS[1] - PS[-1])

    print('sim num= ' + str(inum) + ' ', 'delta= ' + str(delta_cur) + ' ')

    print('Finished!', 'simulation time')
    timee = time.time() - simulation_time
    print("--- %s seconds ---" % (timee))
    return timee

    print('Vis is turned off')
    # Vis.vis_N_2D(system, inum, delta_cur, 'Progons', dir_n)
    # MAIN VISUALISER CALL!!!!! ^^^^

    if field == True:
        Vis.vis_N_2D(system, inum, delta_cur, 'Field', dir_n)
    # Vis.vis_N_3D(galaxy).show
    # Vis.vis_N_anim(galaxy, enn).save('Galaxy.gif', writer='imagemagic', fps=60)


def progons(method, objects, dir, end, dt, delta_step, k, delta_start, delta_end, pulse_table, dir_n):
    progons_global_time = time.time()

    delta_cur = delta_start
    while delta_cur <= delta_end:
        for inum in range(0, k):
            simul(method, objects, dir, end, dt, delta_cur, inum, pulse_table, 0, dir_n)
        delta_cur = float(delta_cur) + delta_step

    print('progons_global_time')
    print("--- %s seconds ---" % (time.time() - progons_global_time))


# MATRIX FUNCTIONS

def openCL_mult(matrix1, matrix2):
    ctx = cl.create_some_context()
    queue = cl.CommandQueue(ctx)

    mf = cl.mem_flags
    a_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=matrix1)
    b_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=matrix2)
    dest_buf = cl.Buffer(ctx, mf.WRITE_ONLY, matrix1.nbytes)

    prg = cl.Program(ctx, """
        __kernel void multiplymatrices(const unsigned int size, __global float * matrix1, __global float * matrix2, __global float * res) {

        int i = get_global_id(1); 
        int j = get_global_id(0);

        res[i + size * j] = 0;

        for (int k = 0; k < size; k++)
        {
            res[i + size * j] += matrix1[k + size * i] * matrix2[j + size * k];
        }

        }
        """).build()
    # res[i + size * j] += matrix1[i + size * k] * matrix2[k + size * j];

    t0 = datetime.datetime.now()

    prg.multiplymatrices(queue, matrix1.shape, None, np.int32(len(matrix1)), a_buf, b_buf, dest_buf)

    final_matrix = np.empty_like(matrix1)
    cl.enqueue_copy(queue, final_matrix, dest_buf)

    # print(final_matrix)

    delta_t = datetime.datetime.now() - t0
    print('OpenCL Multiplication: ' + str(delta_t))

    return final_matrix


def np_mult(matrix1, matrix2):  # =m1 x m2, порядок как в письме
    return matrix1.dot(matrix2)
    # return np.matmul(matrix1, matrix2)


def gravec(r1, r2):  # единичный вектор направления силы, действующей на тело, делённый на квадрат расстояния
    # r1, r2 - коордирнаты тел
    d = dist(r1, r2)
    # print(d)
    if d == 0.0:
        return v([0, 0])
    else:
        # print('Dev', r2-r1)
        return v((r2 - r1) / d ** 3)


def unit_vectors_matrix(position_vectors):  # расчёт матрицы единичных векторов сил, действующих от тела j на тело i
    matrix = []  # собираем матрицу R_ij
    for j in position_vectors:
        line = []
        for i in position_vectors:
            # print('gravec', gravec(i, j))
            line.append(gravec(i, j))
            # print('line', line)
        matrix.append(line)
    # print('rs_m', matrix, 'rs_m end')
    return v(matrix)


# def calc_a(matrix):

def simulation(method, matrices, dir, end, h):
    test1_time = time.time()

    r_sys_mx = []
    v_sys_mx = []
    a_sys_mx = []
    # метод эйлера
    v_sys_mx.append(matrices[3])
    r_sys_mx.append(matrices[2])
    # print('poses ', unit_vectors_matrix(matrices[2]))
    # print('invs ', matrices[1])
    # a_sys_mx.append(( G*(matrices[0]).dot((matrices[1]).dot(unit_vectors_matrix(matrices[2]))) )[0])
    # a_sys_mx.append(( G*nbl.np_mult(matrices[0], nbl.np_mult(matrices[1], unit_vectors_matrix(matrices[2]))) ) [0])
    a_sys_mx.append((G * openCL_mult(matrices[0], openCL_mult(matrices[1], unit_vectors_matrix(matrices[2]))))[0])
    # перемножаем соответственно матрицу произведений масс, матрицу обратных масс, матрица граввеков
    # print('s 0')

    num = int(end / h)  # количесвто шагов
    for i in range(1, num):
        # a_sys_mx.append(( G*(matrices[0]).dot((matrices[1]).dot(unit_vectors_matrix(r_sys_mx[i-1]))) )[0])
        a_sys_mx.append((G * np_mult(matrices[0], np_mult(matrices[1], unit_vectors_matrix(r_sys_mx[i - 1]))))[0])
        # a_sys_mx.append((G * nbl.openCL_mult(matrices[0], nbl.openCL_mult(matrices[1], unit_vectors_matrix(r_sys_mx[i-1]))))[0])
        v_sys_mx.append(v_sys_mx[i - 1] + h * a_sys_mx[i])
        r_sys_mx.append(r_sys_mx[i - 1] + h * v_sys_mx[i])
        # print('s ', i)
    print(r_sys_mx[num - 1])
    print('Finished!')
    print('test1_time')
    timee = time.time() - test1_time
    print("--- %s seconds ---" % (timee))
    return timee