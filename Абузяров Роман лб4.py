from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, Set, List, Optional, Any


# ==================== Задание 1: Иерархия пользовательских исключений ====================
class CustomError(BaseException):
    """Базовое пользовательское исключение"""
    pass


class QuestError(CustomError):
    """Ошибка, связанная с заданиями"""
    pass


class MitaError(CustomError):
    """Ошибка, связанная с Митами"""
    pass


class TraitError(CustomError):
    """Ошибка, связанная с чертами"""
    pass


# ==================== Базовые классы ====================
class Entity(ABC):
    """Абстрактный класс для всех сущностей в игре"""

    entity_count = 0  # Статическое поле для подсчета всех сущностей

    def __init__(self, name: str):
        self._name = name  # Защищенный атрибут
        Entity.entity_count += 1
        self.id = Entity.entity_count

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        """Сеттер для защищенного атрибута"""
        if not isinstance(value, str) or len(value) < 2:
            raise CustomError("Имя должно быть строкой длиной не менее 2 символов")
        self._name = value

    @abstractmethod
    def get_info(self) -> str:
        pass

    @staticmethod
    def get_total_entities() -> int:
        """Статический метод для получения общего количества сущностей"""
        return Entity.entity_count

    def __del__(self):
        Entity.entity_count -= 1

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"


# ==================== Задание 3: Наследование ====================
class BaseMita(Entity):

    def __init__(self, name: str, power: int = 1):
        super().__init__(name)
        self.power = power

    def get_info(self) -> str:
        return f"Базовая Мита: {self.name} (Сила: {self.power})"

    def attack(self):
        return f"{self.name} атакует с силой {self.power}"

    def special_ability(self):
        return "Базовая способность"


class EnhancedMita(BaseMita):

    def __init__(self, name: str, power: int = 1, bonus: int = 0):
        super().__init__(name, power)
        self.bonus = bonus

    # Переопределение метода
    def get_info(self) -> str:
        return f"Улучшенная Мита: {self.name} (Сила: {self.power}, Бонус: {self.bonus})"

    # Использование метода базового класса
    def attack(self):
        base_attack = super().attack()
        return f"{base_attack} и получает бонус {self.bonus}"

    # Новый метод, использующий оба метода
    def combo_attack(self, use_special: bool):
        if use_special:
            return f"{self.special_ability()} -> {self.attack()}"
        else:
            return f"{self.attack()} -> {self.special_ability()}"


# ==================== Класс черт ====================
class Trait(Entity):
    """Класс уникальных черт/способностей Мит"""

    trait_types = defaultdict(set)  # Статическое поле для хранения черт по типам

    def __init__(self, name: str, description: str, effect: str, trait_type: str):
        super().__init__(name)
        self.description = description
        self.effect = effect
        self.trait_type = trait_type
        Trait.trait_types[trait_type].add(name)

    def get_info(self) -> str:
        return f"{self.name} ({self.trait_type}): {self.description}"

    def __str__(self):
        return f"{self.name}: {self.description} (Эффект: {self.effect})"

    @staticmethod
    def get_traits_by_type(trait_type: str) -> Set[str]:
        """Статический метод для получения черт по типу"""
        return Trait.trait_types.get(trait_type, set())

    def __eq__(self, other):
        if not isinstance(other, Trait):
            return False
        return (self.name == other.name and
                self.description == other.description and
                self.effect == other.effect)

    def __add__(self, other):
        """Перегрузка оператора + для создания комбинированной черты"""
        if not isinstance(other, Trait):
            raise TraitError("Можно комбинировать только черты")
        new_name = f"{self.name}+{other.name}"
        new_desc = f"Комбинация {self.name} и {other.name}"
        new_effect = f"{self.effect} и {other.effect}"
        new_type = f"Комбинированная ({self.trait_type}+{other.trait_type})"
        return Trait(new_name, new_desc, new_effect, new_type)

    def __repr__(self):
        return (f"Trait(name='{self.name}', description='{self.description}', "
                f"effect='{self.effect}', trait_type='{self.trait_type}')")


# ==================== Класс заданий ====================
class Quest(Entity):
    """Класс заданий/целей Мит"""

    quest_difficulties = {}  # Статическое поле для хранения сложности заданий

    def __init__(self, name: str, description: str, reward: str,
                 is_completed: bool = False, difficulty: str = "Обычный"):
        super().__init__(name)
        self.description = description
        self.reward = reward
        self.is_completed = is_completed
        self.difficulty = difficulty
        Quest.quest_difficulties[name] = difficulty

    def get_info(self) -> str:
        status = "Выполнено" if self.is_completed else "Активно"
        return f"[{status}] {self.name}: {self.description} (Сложность: {self.difficulty})"

    def complete(self):
        self.is_completed = True
        return f"Задание '{self.name}' выполнено! Награда: {self.reward}"

    def __str__(self):
        status = "Выполнено" if self.is_completed else "Активно"
        return f"[{status}] {self.name}: {self.description}"

    def __lt__(self, other):
        """Перегрузка оператора < для сравнения по сложности"""
        if not isinstance(other, Quest):
            raise QuestError("Можно сравнивать только задания")
        difficulties = {"Легкий": 1, "Обычный": 2, "Сложный": 3, "Очень сложный": 4}
        return difficulties.get(self.difficulty, 0) < difficulties.get(other.difficulty, 0)

    def __contains__(self, item):
        """Перегрузка оператора in для поиска подстроки в описании задания"""
        return item in self.description or item in self.name

    def __repr__(self):
        return (f"Quest(name='{self.name}', description='{self.description}', "
                f"reward='{self.reward}', is_completed={self.is_completed}, "
                f"difficulty='{self.difficulty}')")


# ==================== Класс Мит ====================
class Mita(Entity):
    """Базовый класс Миты"""

    mitas_by_type = defaultdict(set)  # Статическое поле для хранения Мит по типам

    def __init__(self, name: str, description: str, traits: List[Trait],
                 quests: List[Quest], mita_type: str = "Обычная"):
        super().__init__(name)
        self.description = description
        self.traits = traits
        self.quests = quests
        self.is_active = True
        self.mita_type = mita_type
        Mita.mitas_by_type[mita_type].add(name)

    def get_info(self) -> str:
        return f"Мита: {self.name} (Тип: {self.mita_type})"

    def add_trait(self, trait: Trait):
        self.traits.append(trait)

    def add_quest(self, quest: Quest):
        self.quests.append(quest)

    def get_active_quests(self):
        return [q for q in self.quests if not q.is_completed]

    def complete_quest(self, quest_title: str):
        for quest in self.quests:
            if quest.name == quest_title and not quest.is_completed:
                return quest.complete()
        return "Задание не найдено или уже выполнено"

    def __str__(self):
        traits_str = "\n".join(str(t) for t in self.traits)
        quests_str = "\n".join(str(q) for q in self.quests)
        return (f"Мита: {self.name}\nТип: {self.mita_type}\n"
                f"Описание: {self.description}\n\nЧерты:\n{traits_str}\n\nЗадания:\n{quests_str}")

    def __getitem__(self, key):
        """Перегрузка оператора [] для доступа к чертам и заданиям по индексу"""
        if isinstance(key, int):
            if 0 <= key < len(self.traits):
                return self.traits[key]
            elif 0 <= key < len(self.quests):
                return self.quests[key]
            else:
                raise IndexError("Индекс вне диапазона")
        elif isinstance(key, str):
            for trait in self.traits:
                if trait.name == key:
                    return trait
            for quest in self.quests:
                if quest.name == key:
                    return quest
            raise KeyError(f"Черта или задание с именем '{key}' не найдены")
        else:
            raise TypeError("Ключ должен быть int или str")

    @staticmethod
    def get_mitas_by_type(mita_type: str) -> Set[str]:
        """Статический метод для получения Мит по типу"""
        return Mita.mitas_by_type.get(mita_type, set())

    def __repr__(self):
        traits_repr = ", ".join(repr(t) for t in self.traits)
        quests_repr = ", ".join(repr(q) for q in self.quests)
        return (f"Mita(name='{self.name}', description='{self.description}', "
                f"traits=[{traits_repr}], quests=[{quests_repr}], "
                f"mita_type='{self.mita_type}')")


# ==================== Класс игрока ====================
class Player(Entity):
    """Класс игрока"""

    max_level = 100  # Статическое поле для максимального уровня

    def __init__(self, name: str, level: int = 1):
        super().__init__(name)
        self.level = level
        self.completed_quests = set()  # Используем множество вместо списка
        self.active_quests = set()
        self.encountered_mitas = set()
        self.traits = defaultdict(int)  # Словарь для хранения черт и их уровней

    def get_info(self) -> str:
        return (f"Игрок: {self.name} (Уровень: {self.level}/{Player.max_level})\n"
                f"Активные задания: {len(self.active_quests)}\n"
                f"Завершенные задания: {len(self.completed_quests)}")

    def encounter_mita(self, mita: Mita):
        if mita not in self.encountered_mitas:
            self.encountered_mitas.add(mita)
            for quest in mita.get_active_quests():
                self.active_quests.add(quest)
            return f"Вы встретили новую Миту: {mita.name}"
        return f"Вы снова встретили Миту: {mita.name}"

    def complete_quest(self, quest_title: str):
        for quest in self.active_quests:
            if quest.name == quest_title:
                result = quest.complete()
                self.completed_quests.add(quest)
                self.active_quests.remove(quest)
                self.level_up()
                return f"{result}\nУровень повышен до {self.level}!"
        return "Задание не найдено среди активных"

    def level_up(self):
        if self.level < Player.max_level:
            self.level += 1
            return True
        return False

    def add_trait(self, trait: Trait, level: int = 1):
        self.traits[trait.name] = level

    def __str__(self):
        return self.get_info()

    def __iadd__(self, levels: int):
        """Перегрузка оператора += для увеличения уровня"""
        if not isinstance(levels, int):
            raise ValueError("Можно добавлять только целые уровни")
        self.level = min(self.level + levels, Player.max_level)
        return self

    def __call__(self, message: str):
        """Перегрузка оператора () для отправки сообщения игроку"""
        return f"Сообщение для {self.name}: {message}"

    def __repr__(self):
        return (f"Player(name='{self.name}', level={self.level}, "
                f"completed_quests={list(self.completed_quests)}, "
                f"active_quests={list(self.active_quests)})")


# ==================== Класс игрового мира ====================
class World:
    """Класс игрового мира"""

    instance = None  # Статическое поле для реализации Singleton

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.mitas = set()
            cls.instance.players = set()
        return cls.instance

    def add_mita(self, mita: Mita):
        self.mitas.add(mita)

    def add_player(self, player: Player):
        self.players.add(player)

    def get_mita_by_name(self, name: str) -> Optional[Mita]:
        for mita in self.mitas:
            if mita.name == name:
                return mita
        return None

    def get_player_by_name(self, name: str) -> Optional[Player]:
        for player in self.players:
            if player.name == name:
                return player
        return None

    def __str__(self):
        return (f"Игровой мир (Singleton)\n"
                f"Миты: {len(self.mitas)}\n"
                f"Игроки: {len(self.players)}\n"
                f"Всего сущностей: {Entity.get_total_entities()}")

    def __iter__(self):
        """Перегрузка оператора итерации для обхода всех Мит и игроков"""
        all_entities = list(self.mitas) + list(self.players)
        return iter(all_entities)

    def __repr__(self):
        mitas_repr = ", ".join(repr(m) for m in self.mitas)
        players_repr = ", ".join(repr(p) for p in self.players)
        return f"World(mitas=[{mitas_repr}], players=[{players_repr}])"


# ==================== Задание 2: Работа с массивами объектов ====================
class ObjectArrayDemo:
    """Демонстрация работы с массивами объектов"""

    def __init__(self):
        # Одномерный список объектов Quest
        self.quests_1d = [
            Quest("Поиск сокровищ", "Найти древний артефакт", "100 золота", False, "Легкий"),
            Quest("Охота на дракона", "Победить древнего дракона", "Драконья броня", False, "Очень сложный"),
            Quest("Спасение деревни", "Защитить деревню от бандитов", "Благодарность жителей", True, "Обычный")
        ]

        # Двумерный список объектов Trait
        self.traits_2d = [
            [
                Trait("Сила", "Увеличивает физическую силу", "+10 к силе", "Физическая"),
                Trait("Ловкость", "Увеличивает ловкость", "+10 к ловкости", "Физическая")
            ],
            [
                Trait("Мудрость", "Увеличивает мудрость", "+10 к мудрости", "Магическая"),
                Trait("Интеллект", "Увеличивает интеллект", "+10 к интеллекту", "Магическая")
            ]
        ]

    def find_max_difficulty_quest(self, quests: List[Quest]) -> Optional[Quest]:
        """Находит задание с максимальной сложностью в одномерном списке"""
        if not quests:
            return None
        return max(quests,
                   key=lambda q: {"Легкий": 1, "Обычный": 2, "Сложный": 3, "Очень сложный": 4}.get(q.difficulty, 0))

    def find_max_in_2d(self, attr: str) -> Any:
        """Находит максимальное значение атрибута в двумерном списке черт"""
        max_value = None
        for row in self.traits_2d:
            for trait in row:
                try:
                    value = getattr(trait, attr)
                    if max_value is None or value > max_value:
                        max_value = value
                except AttributeError:
                    continue
        return max_value

    def demo(self):
        """Демонстрация работы с массивами"""
        print("\n=== Демонстрация работы с массивами объектов ===")

        # Одномерный список
        print("\nОдномерный список заданий:")
        for quest in self.quests_1d:
            print(quest)

        max_quest = self.find_max_difficulty_quest(self.quests_1d)
        print(f"\nСамое сложное задание: {max_quest.name} ({max_quest.difficulty})")

        # Двумерный список
        print("\nДвумерный список черт:")
        for i, row in enumerate(self.traits_2d):
            print(f"Ряд {i}:")
            for trait in row:
                print(f"  {trait}")

        max_name = self.find_max_in_2d("name")
        print(f"\nМаксимальное имя (лексикографически): {max_name}")


# ==================== Задание 1: Обработка исключений ====================
def exception_handling_demo():
    """Демонстрация обработки исключений"""
    print("\n=== Демонстрация обработки исключений ===")
    world = World()

    try:
        print("\nПопытка получить несуществующую Миту:")
        non_existent = world.get_mita_by_name("Несуществующая")
        print(non_existent.name)
    except AttributeError as e:
        print(f"Ошибка AttributeError: {e} - Мита не найдена")
    finally:
        print("Этот блок выполнится в любом случае")

    # Генерация собственного исключения
    try:
        print("\nПопытка создать игрока с некорректным именем:")
        player = Player("A")  # Слишком короткое имя
    except CustomError as e:
        print(f"Поймано пользовательское исключение: {e}")

    # Обработка разных типов исключений
    try:
        print("\nПопытка выполнить различные операции:")
        quest = Quest("Тест", "Тестовое описание", "Награда")
        print(quest < "Не задание")  # Вызовет QuestError

        trait = Trait("Сила", "Описание", "Эффект", "Тип")
        print(trait + "Не черта")  # Вызовет TraitError

    except QuestError as e:
        print(f"Ошибка задания: {e}")
    except TraitError as e:
        print(f"Ошибка черты: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")


# ==================== Демонстрация работы со строками ====================
def process_string_demo():
    """Демонстрация работы со строками"""
    print("\n=== Демонстрация работы со строками ===")
    text = "Огненная Мита, Хранитель пламени"
    print(f"Исходная строка: {text}")
    print(f"Верхний регистр: {text.upper()}")
    print(f"Замена: {text.replace('Мита', 'Сущность')}")
    print(f"Разделение: {text.split(', ')}")
    print(f"Поиск 'Хранитель': {'Хранитель' in text}")


# ==================== Основная функция ====================
def main():
    # Демонстрация Singleton для World
    world1 = World()
    world2 = World()
    print(f"world1 is world2: {world1 is world2}")  # Должно быть True

    # Создаем уникальные черты для Мит
    fire_trait = Trait("Огненная аура", "Мита окружена пламенем", "Наносит урон при приближении", "Огонь")
    healing_trait = Trait("Исцеляющий свет", "Мита излучает целебную энергию", "Восстанавливает здоровье", "Свет")
    shadow_trait = Trait("Теневой шаг", "Мита может перемещаться через тени", "Может телепортироваться", "Тень")

    # Демонстрация комбинирования черт (перегрузка оператора +)
    combined_trait = fire_trait + shadow_trait
    print(f"\nКомбинированная черта: {combined_trait}")

    # Демонстрация статических методов
    print("\nЧерты типа 'Огонь':", Trait.get_traits_by_type("Огонь"))

    # Создаем задания для Мит
    fire_quest1 = Quest(name="Пламя возмездия", description="Найти и наказать предателя", reward="Огненный меч",
                        is_completed=False, difficulty="Сложный")
    fire_quest2 = Quest("Испытание жаром", "Пройти через огненный лабиринт", "Устойчивость к огню", False,
                        "Очень сложный")

    healing_quest1 = Quest("Исцеление ран", "Помочь 10 раненым", "Благословение здоровья", False, "Обычный")
    shadow_quest1 = Quest("Теневой контракт", "Устранить цель скрытно", "Теневой плащ", False, "Сложный")

    # Демонстрация сравнения заданий (перегрузка оператора <)
    print(f"\nСравнение заданий: {fire_quest1.name} < {healing_quest1.name}: {fire_quest1 < healing_quest1}")

    # Демонстрация поиска в задании (перегрузка оператора in)
    print(f"'лабиринт' в задании {fire_quest2.name}: {'лабиринт' in fire_quest2}")

    # Создаем Миты
    fire_mita = Mita("Игнис", "Огненная Мита, хранитель пламени", [fire_trait, combined_trait],
                     [fire_quest1, fire_quest2], "Огненная")
    healing_mita = Mita("Люмин", "Целительная Мита, дарующая жизнь", [healing_trait], [healing_quest1], "Светлая")
    shadow_mita = Mita("Умбрис", "Теневая Мита, мастер скрытности", [shadow_trait], [shadow_quest1], "Теневая")

    # Добавляем Миты в мир
    world1.add_mita(fire_mita)
    world1.add_mita(healing_mita)
    world1.add_mita(shadow_mita)

    # Демонстрация статических методов для Мит
    print("\nМиты типа 'Огненная':", Mita.get_mitas_by_type("Огненная"))

    # Создаем игрока
    player = Player("Аэрин")
    world1.add_player(player)

    # Демонстрация перегрузки оператора += для игрока
    player += 5
    print(f"\nУровень игрока после += 5: {player.level}")

    # Демонстрация перегрузки оператора () для игрока
    print(player("Добро пожаловать в игру!"))

    # Демонстрация перегрузки оператора [] для Миты
    print(f"\nПервая черта Игниса: {fire_mita[0]}")
    print(f"Задание 'Пламя возмездия' у Игниса: {fire_mita['Пламя возмездия']}")

    # Взаимодействия игрока с миром
    print("\n=== Игрок встречает Мит ===")
    print(player.encounter_mita(fire_mita))
    print(player.encounter_mita(healing_mita))

    print("\n=== Информация о игроке ===")
    print(player)

    print("\n=== Выполнение заданий ===")
    print(player.complete_quest("Пламя возмездия"))
    print(player.complete_quest("Исцеление ран"))

    print("\n=== Информация о игроке после выполнения заданий ===")
    print(player)

    print("\n=== Информация о Мите Игнис ===")
    print(fire_mita)

    print("\n=== Состояние игрового мира ===")
    print(world1)

    # Демонстрация работы с динамическими структурами данных
    print("\n=== Демонстрация работы с множествами ===")
    player.add_trait(fire_trait, 2)
    player.add_trait(healing_trait, 1)
    print(f"Черты игрока: {dict(player.traits)}")

    # Демонстрация итерации по миру (перегрузка оператора итерации)
    print("\n=== Все сущности в мире ===")
    for entity in world1:
        print(f"- {entity.name} ({entity.__class__.__name__})")

    # Демонстрация работы со строками
    process_string_demo()

    # Демонстрация обработки исключений
    exception_handling_demo()

    # Демонстрация работы с массивами объектов
    array_demo = ObjectArrayDemo()
    array_demo.demo()

    # Демонстрация наследования
    print("\n=== Демонстрация наследования ===")
    base_mita = BaseMita("Базовая", 10)
    enhanced_mita = EnhancedMita("Улучшенная", 15, 5)

    print(base_mita.get_info())
    print(enhanced_mita.get_info())

    print("\nАтака базовой Миты:", base_mita.attack())
    print("Атака улучшенной Миты:", enhanced_mita.attack())

    print("\nКомбинированная атака (с особой способностью):", enhanced_mita.combo_attack(True))
    print("Комбинированная атака (без особой способности):", enhanced_mita.combo_attack(False))

    # Демонстрация защищенных атрибутов
    print("\n=== Демонстрация защищенных атрибутов ===")
    try:
        print("Попытка прямого доступа к _name:", end=" ")
        print(base_mita._name)  # Технически возможно, но не рекомендуется
    except Exception as e:
        print(f"Ошибка: {e}")

    print("Доступ через геттер:", base_mita.name)

    try:
        print("Попытка установки некорректного имени:")
        base_mita.name = ""  # Вызовет исключение
    except CustomError as e:
        print(f"Поймано исключение: {e}")

    # Демонстрация repr и eval
    print("\n=== Демонстрация repr и eval ===")
    print("repr для Quest:", repr(fire_quest1))

    # Создание нового объекта из repr строки
    quest_repr = repr(fire_quest1)
    try:
        new_quest = eval(quest_repr)
        print("\nСозданный из repr объект:", new_quest)
        print("Тип созданного объекта:", type(new_quest))
    except Exception as e:
        print(f"Ошибка при создании объекта: {e}")

    print(f"\nВсего создано сущностей: {Entity.get_total_entities()}")


if __name__ == "__main__":
    main()