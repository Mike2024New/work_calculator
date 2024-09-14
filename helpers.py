def count_elements(input_collect: list | tuple | set) -> list:
    """
    Принимает на вход коллекцию с повторяющимися элементами и возвращает коллекцию
    с количеством уникальных элементов (то есть подсчитывает кол-во каждого элемента в входной коллекции)
    все дубли удаляются. Порядок коллекции сохраняется тот же что и в исходной коллекции (с учетом удаленных дублей).

    :param input_collect: list, tuple,set - входная коллекция с элементами
    :return: список с кортежами вида (element:count)
    =======================================================================
    Пример использования:
    res=count_elements(['a', 'b', 'c', 'a', 'b'])
    на выходе res будет равно: [('a', 2), ('b', 2), ('c', 1)]
    """
    element_count = {}  # словарь хранит уникальные элементы и их кол-во
    for element in input_collect:
        if element in element_count:
            element_count[element] += 1  # если элемент уже есть в коллекции увелич счётчик.
        else:
            element_count[element] = 1  # если нет, то записать элемент в словарь с начальным 1
    return [(element, count) for element, count in element_count.items()]  # вернуть список с кортежами


def debug_output_console_mark_function_and_args(fillchar: str = '=', width: int = 80, **kwargs) -> callable:
    """
    функция для отладки, выводит метки старта и завершения в консоль
    :type kwargs: object -> принимает на вход отслеживаемые аргументы
    :param fillchar: символ заливки
    :param width: -> Длина заливки символов в консоли
    :return:
    пример, есть функция:
    def test():
        print(123)

    Вывод которой в консоль выглядит так: 123
    Подключили декоратор:

    @output_console_mark_function(fillchar="*",x=1,y=2)
    def test():
        print(123)

    Теперь вывод выглядит так:
    ************************* test *************************
    аргументы на входе:
    x:1
    y:2
    -------------
    Тело функции:
    123
    ************************* end test *********************
    """

    def decorator(func: callable) -> callable:
        def inner() -> None:
            try:
                func_name_start = func.__name__.upper()
                func_name_end = f" end {func_name_start} "
                count_char_start = int((width - len(func_name_start)) / 2)
                count_char_end = int((width - len(func_name_end)) / 2)
                print(f"{fillchar * count_char_start}{func_name_start}{fillchar * count_char_start}")
                if kwargs:
                    print("аргументы на входе:")
                    [print(f"{key}:{kwargs[key]}") for key in kwargs]
                    print(f"{'-' * 19}\nТело функции:")
                func()  # ВЫПОЛНЕНИЕ ПЕРЕДАННОЙ ФУНКЦИИ
                print(f"{fillchar * count_char_end}{func_name_end}{fillchar * count_char_end}")
            except Exception as err:
                print(f"Произошла ошибка debug_output_console_mark_function_and_args -> {err}")
                func()  # ВЫПОЛНЕНИЕ ПЕРЕДАННОЙ ФУНКЦИИ

        return inner

    return decorator