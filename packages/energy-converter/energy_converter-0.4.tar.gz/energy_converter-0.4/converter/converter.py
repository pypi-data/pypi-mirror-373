import pandas as pd
import calendar

def convert(date_col, df,
            initial_interval, target_interval,
            initial_unit, target_unit):
    # Проверка столбца даты
    if date_col not in df.columns:
        print(f"Столбец '{date_col}' не найден.")
        return None

    df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.tz_localize(None)
    time_mapping = {
        '1min':   1,
        '5min':   5,
        '15min':  15,
        '60min':  60,
        '1day':   1440,
        '1month': 'M',
        '1year':  'Y'
    }

    if initial_interval not in time_mapping or target_interval not in time_mapping:
        print("Неверные интервалы:", initial_interval, target_interval)
        return None

    init_val = time_mapping[initial_interval]
    tgt_val  = time_mapping[target_interval]

    # -----------------------------------------------------------------
    # 2. Проверяем, numeric ли оба интервала, или календарный
    # -----------------------------------------------------------------
    numeric_intervals = {1,5,15,60,1440}
    # если оба init_val и tgt_val - числа => ваша логика
    # иначе => календарная логика
    def is_numeric(v):
        return isinstance(v,int) or isinstance(v,float)

    both_numeric = is_numeric(init_val) and is_numeric(tgt_val)

    # -----------------------------------------------------------------
    # 3. Если оба ЧИСЛОВЫЕ - Ваша логика
    # -----------------------------------------------------------------
    if both_numeric:
        # Ниже — ваш исходный код, БЕЗ ИЗМЕНЕНИЙ.
        initial_interval_minutes = init_val
        target_interval_minutes  = tgt_val

        # ----- Случай 1: kWh -> kWh -----
        if initial_unit == 'kwh' and target_unit == 'kwh':
            if initial_interval_minutes > target_interval_minutes:
                # "Разбиваем" большую гранулярность на более мелкую
                expanded_rows = []
                # Во сколько раз нужно разбить
                num_intervals = initial_interval_minutes // target_interval_minutes

                for _, row in df.iterrows():
                    for i in range(num_intervals):
                        new_row = row.copy()
                        new_row[date_col] = row[date_col] + pd.Timedelta(minutes=target_interval_minutes * i)
                        for col in df.columns:
                            if col != date_col:
                                # Делим количество kWh на число более мелких интервалов
                                new_row[col] = row[col] / num_intervals
                        expanded_rows.append(new_row)

                df_expanded = pd.DataFrame(expanded_rows)
                return df_expanded

            else:
                # При укрупнении интервала (или равенстве) - суммируем
                df_resampled = (
                    df
                    .set_index(date_col)
                    .resample(f'{target_interval_minutes}T').fillna(method='ffill').fillna(method='bfill')
                    .reset_index()
                )
                return df_resampled

            # ----- Случай 2: kW -> kW -----
            # При уменьшении интервала (был больше, стал меньше) - просто дублируем (мощность не делим)
            # При увеличении интервала - берём среднее (т.к. мощность при укрупнении обычно усредняют)
        elif initial_unit == 'kw' and target_unit == 'kw':
            if initial_interval_minutes > target_interval_minutes:
                # "Разбиваем" (исходный интервал крупнее целевого) - дублируем
                expanded_rows = []
                num_intervals = initial_interval_minutes // target_interval_minutes

                for _, row in df.iterrows():
                    for i in range(num_intervals):
                        new_row = row.copy()
                        new_row[date_col] = row[date_col] + pd.Timedelta(minutes=target_interval_minutes * i)
                        # Значения в kW просто копируем, не делим
                        expanded_rows.append(new_row)

                df_expanded = pd.DataFrame(expanded_rows)
                return df_expanded
            else:
                # Укрупняем интервал или оставляем такой же - берём среднее мощности
                df_resampled = (
                    df
                    .set_index(date_col)
                    .resample(f'{target_interval_minutes}T')
                    .mean()
                    .reset_index()
                )
                return df_resampled

            # ----- Случай 3: kW -> kWh -----
        elif initial_unit == 'kw' and target_unit == 'kwh':
            expanded_rows = []
            num_intervals = initial_interval_minutes // target_interval_minutes  # 24
            num_intervals2 = 60 / initial_interval_minutes
            num_intervals3 = 60 / target_interval_minutes  # 1
            num_intervals4 = initial_interval_minutes / 60
            num_intervals5 = target_interval_minutes / 60

            if initial_interval_minutes > target_interval_minutes:
                for _, row in df.iterrows():
                    for i in range(num_intervals):
                        new_row = row.copy()
                        new_row[date_col] = row[date_col] + pd.Timedelta(minutes=target_interval_minutes * i)
                        for col in df.columns:
                            if col != date_col:
                                if initial_interval_minutes <= 60:
                                    new_row[col] = row[col] / (num_intervals * num_intervals2)
                                elif initial_interval_minutes > 60:
                                    new_row[col] = row[col] * num_intervals5
                        expanded_rows.append(new_row)

                df_expanded = pd.DataFrame(expanded_rows)
                return df_expanded
            elif initial_interval_minutes == target_interval_minutes:
                # Просто делим значения в столбцах на количество интервалов, если интервалы одинаковые
                df_copy = df.copy()  # Создаём копию DataFrame для изменений
                for col in df.columns:
                    if col != date_col:
                        if initial_interval_minutes <= 60:
                            df_copy[col] = df_copy[col] / num_intervals2
                        elif initial_interval_minutes > 60:
                            df_copy[col] = df_copy[col] * num_intervals4

                return df_copy
            elif initial_interval_minutes < target_interval_minutes:
                df_copy = df.copy()  # Создаём копию DataFrame для изменений
                for col in df.columns:
                    if col != date_col:
                        if initial_interval_minutes <= 60:
                            df_copy[col] = df_copy[col] / num_intervals2
                        elif initial_interval_minutes > 60:
                            df_copy[col] = df_copy[col] * num_intervals4
                df_resampled = (
                    df_copy
                    .set_index(date_col)  # Устанавливаем столбец с датой как индекс
                    .resample(f'{target_interval_minutes}T')  # Ресемплинг по целевому интервалу
                    .sum()  # Суммируем значения по целевому интервалу
                    .reset_index()  # Сбрасываем индекс, чтобы дата снова была столбцом
                )
                return df_resampled

            # ----- Случай 4: kWh -> kW-----
        elif initial_unit == 'kwh' and target_unit == 'kw':
            expanded_rows = []
            num_intervals = initial_interval_minutes // target_interval_minutes  # 24
            num_intervals2 = 60 / initial_interval_minutes
            num_intervals3 = 60 / target_interval_minutes  # 1
            num_intervals4 = initial_interval_minutes / 60
            num_intervals5 = target_interval_minutes / 60
            if initial_interval_minutes > target_interval_minutes:
                df_copy = df.copy()  # Создаём копию DataFrame для изменений
                for col in df.columns:
                    if col != date_col:
                        if initial_interval_minutes <= 60:
                            df_copy[col] = df_copy[col] * num_intervals2
                        elif initial_interval_minutes > 60:
                            df_copy[col] = df_copy[col] / num_intervals4
                for _, row in df_copy.iterrows():
                    for i in range(num_intervals):
                        new_row = row.copy()
                        new_row[date_col] = row[date_col] + pd.Timedelta(minutes=target_interval_minutes * i)
                        # Значения в kW просто копируем, не делим
                        expanded_rows.append(new_row)
                df_expanded = pd.DataFrame(expanded_rows)
                return df_expanded
            elif initial_interval_minutes == target_interval_minutes:
                df_copy = df.copy()
                for col in df.columns:
                    if col != date_col:
                        if initial_interval_minutes <= 60:
                            df_copy[col] = df_copy[col] * num_intervals2
                        elif initial_interval_minutes > 60:
                            df_copy[col] = df_copy[col] / num_intervals4
                return df_copy
            elif initial_interval_minutes < target_interval_minutes:
                df_copy = df.copy()
                for col in df.columns:
                    if col != date_col:
                        df_copy[col] = df_copy[col] * num_intervals2
                df_resampled = (
                    df_copy
                    .set_index(date_col)
                    .resample(f'{target_interval_minutes}T')
                    .mean()
                    .reset_index()
                )
                return df_resampled
        else:
            print("Неизвестная комбинация")
            return None

    # -----------------------------------------------------------------
    # 4. Если один или оба интервала = '1month'/'1year'
    #    => календарная логика, учитывая реальную длину месяцев/лет
    # -----------------------------------------------------------------

    # Вспомогательная функция: "укрупнить" (downsample) => .resample('M'/'Y')
    # Выбираем sum() для kWh, mean() для kW (по аналогии с вашей логикой).
    def calendar_aggregate(df_in, freq_alias, init_unit, tgt_unit):
        # freq_alias = 'M' или 'Y'
        if init_unit=='kwh' and tgt_unit=='kwh':
            df_out = df_in.resample(freq_alias).sum()
        elif init_unit=='kw' and tgt_unit=='kw':
            df_out = df_in.resample(freq_alias).mean()
        else:
            print("Неизвестная комбинация")
            return None
        return df_out

    # Функция "дробления" (upsample) из месяца/года в более мелкие интервалы.
    # Равномерное распределение (kWh), дублирование (kW).
    def calendar_expand(df_in, date_col, init_unit, tgt_unit, freq_alias):
        """
        Если исходный интервал = '1month' или '1year',
        а целевой '1day', '60min', '15min' или даже '1month'/'1year' (второе реже нужно),
        "дробим" каждую строку.
        """
        out_rows = []
        numeric_cols = [c for c in df_in.columns if c != date_col]

        # sort по дате — чтобы было удобнее
        df_in = df_in.sort_values(by=date_col).reset_index(drop=True)

        for _, row in df_in.iterrows():
            dt_start = row[date_col]
            if init_val == 'M':
                # Реально начало и конец месяца
                days_in_m = calendar.monthrange(dt_start.year, dt_start.month)[1]
                dt_period_start = dt_start.replace(day=1, hour=0, minute=0, second=0)
                dt_period_end   = dt_start.replace(day=days_in_m, hour=23, minute=59, second=59)
            else:
                # init_val=='Y'
                is_leap = calendar.isleap(dt_start.year)
                days_in_y = 366 if is_leap else 365
                dt_period_start = dt_start.replace(month=1, day=1, hour=0, minute=0, second=0)
                dt_period_end   = dt_start.replace(month=12, day=31, hour=23, minute=59, second=59)

            # freq_alias – это что-то вроде '1D', '60T', '15T', ...
            rng = pd.date_range(start=dt_period_start, end=dt_period_end, freq=freq_alias)
            n_sub = len(rng)
            if n_sub == 0:
                # если вдруг freq_alias слишком крупный
                # тогда хотя бы одну строку оставим (без изменений)
                out_rows.append(row)
                continue

            for i in range(n_sub):
                new_row = row.copy()
                new_row[date_col] = rng[i]

                # Ваш принцип: kWh -> делим, kW -> дублируем
                if init_unit=='kwh' and tgt_unit=='kwh':
                    # делим
                    for c in numeric_cols:
                        new_row[c] = new_row[c] / n_sub
                elif init_unit=='kw' and tgt_unit=='kw':
                    # дублируем
                    pass
                else:
                    print("Неизвестная комбинация")
                    return None

                out_rows.append(new_row)

        df_expanded = pd.DataFrame(out_rows).sort_values(by=date_col).reset_index(drop=True)
        return df_expanded

    # -----------------------------------------------------
    # Собственно календарная ветка:
    # Выясняем, что "чаще" и что "реже"
    # (порядок: '1min'=1 < '5min' < ... < '1day' < '1month'(M) < '1year'(Y))
    # -----------------------------------------------------
    freq_map = {
        1:      ('1T',1),    # 1 min
        5:      ('5T',2),
        15:     ('15T',3),
        60:     ('60T',4),
        1440:   ('1D',5),
        'M':    ('M',6),
        'Y':    ('Y',7)
    }

    def get_order(val):
        return freq_map[val][1]  # второе поле
    def get_freq(val):
        return freq_map[val][0]  # первое поле

    init_order = get_order(init_val)
    tgt_order  = get_order(tgt_val)

    # Ставим df в индекс по дате (для resample)
    df = df.copy()
    df.set_index(date_col, inplace=True)
    df.sort_index(inplace=True)

    if init_order < tgt_order:
        # Исходная частота "чаще" => целевая реже => УКРУПНЕНИЕ = resample
        # (например, 15min->month, day->year, ...)

        df_res = calendar_aggregate(df, get_freq(tgt_val), initial_unit, target_unit)
        if df_res is None:
            return None
        df_res = df_res.reset_index()
        return df_res

    else:
        # init_order > tgt_order => ДРОБИМ (например, month->day, year->month, etc.)
        df.reset_index(inplace=True)
        freq_str = get_freq(tgt_val)  # напр. '15T','1D','M'...
        df_expanded = calendar_expand(df, date_col, initial_unit, target_unit, freq_str)
        return df_expanded
