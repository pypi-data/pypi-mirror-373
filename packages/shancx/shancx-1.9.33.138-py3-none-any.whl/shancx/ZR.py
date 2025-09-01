def dbz2rfl(d):  # 全局定义
    return 10. ** (d / 10.)

def rfl2mmh(z, a=200., b=1.6):  # 全局定义
    return (z / a) ** (1. / b)

def ZR1(conf):
    dbz = conf[0]
    z_values = dbz2rfl(dbz)  # 直接调用全局函数
    rainfall_mmh = rfl2mmh(z_values)
    rainfall_mmh[rainfall_mmh < 0.1] = 0
    return rainfall_mmh