from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, Set, List, Optional


class Entity(ABC):
    """Абстрактный класс для всех сущностей в игре"""

    entity_count = 0  # Статическое поле для подсчета всех сущностей

    def __init__(self, name: str):
        self.name = name
        Entity.entity_count += 1
        self.id = Entity.entity_count

    @abstractmethod
    def get_info(self) -> str:
        pass

    @staticmethod
    def get_total_entities() -> int:
        """Статический метод для получения общего количества сущностей"""
        return Entity.entity_count

    def __del__(self):
        Entity.entity_count -= 1


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
            raise ValueError("Можно комбинировать только черты")
        new_name = f"{self.name}+{other.name}"
        new_desc = f"Комбинация {self.name} и {other.name}"
        new_effect = f"{self.effect} и {other.effect}"
        new_type = f"Комбинированная ({self.trait_type}+{other.trait_type})"
        return Trait(new_name, new_desc, new_effect, new_type)


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
            raise ValueError("Можно сравнивать только задания")
        difficulties = {"Легкий": 1, "Обычный": 2, "Сложный": 3, "Очень сложный": 4}
        return difficulties.get(self.difficulty, 0) < difficulties.get(other.difficulty, 0)

    def __contains__(self, item):
        """Перегрузка оператора in для поиска подстроки в описании задания"""
        return item in self.description or item in self.name


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


def process_string_demo():
    """Демонстрация работы со строками"""
    print("\n=== Демонстрация работы со строками ===")
    text = "Огненная Мита, Хранитель пламени"
    print(f"Исходная строка: {text}")
    print(f"Верхний регистр: {text.upper()}")
    print(f"Замена: {text.replace('Мита', 'Сущность')}")
    print(f"Разделение: {text.split(', ')}")
    print(f"Поиск 'Хранитель': {'Хранитель' in text}")


def exception_handling_demo():
    """Демонстрация обработки исключений"""
    print("\n=== Демонстрация обработки исключений ===")
    world = World()
    try:
        non_existent = world.get_mita_by_name("Несуществующая")
        print(non_existent.name)  # Вызовет исключение
    except AttributeError as e:
        print(f"Ошибка: {e} - Мита не найдена")

    try:
        player = Player("Тест")
        player += "не число"  # Вызовет исключение
    except ValueError as e:
        print(f"Ошибка: {e}")


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
    fire_quest1 = Quest(name="Пламя возмездия", description="Найти и наказать предателя", reward="Огненный меч", is_completed=False, difficulty="Сложный")
    fire_quest2 = Quest("Испытание жаром", "Пройти через огненный лабиринт", "Устойчивость к огню", False,
                        "Очень сложный")

    healing_quest1 = Quest("Исцеление ран", "Помочь 10 раненым", "Благословение здоровья", False, "Обычный")
    shadow_quest1 = Quest("Теневой контракт", "Устранить цель скрытно", "Теневой плащ", False, "Сложный")

    # Демонстрация сравнения заданий (перегрузка оператора <)
    print(f"\nСравнение заданий: {fire_quest1.name} < {healing_quest1.name}: {fire_quest1 < healing_quest1}")

    # И аналогично в других местах, где используется quest.title
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

    process_string_demo()
    exception_handling_demo()

    # Демонстрация абстрактного метода
    print("\n=== Демонстрация абстрактного метода get_info() ===")
    entities = [fire_mita, healing_quest1, player, shadow_trait]
    for entity in entities:
        print(entity.get_info())

    print(f"\nВсего создано сущностей: {Entity.get_total_entities()}")


if __name__ == "__main__":
    main()