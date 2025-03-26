class Trait:
    """Класс уникальных черт/способностей Мит"""

    def __init__(self, name: str, description: str, effect: str):
        self.name = name
        self.description = description
        self.effect = effect

    def __str__(self):
        return f"{self.name}: {self.description} (Эффект: {self.effect})"


class Quest:
    """Класс заданий/целей Мит"""

    def __init__(self, title: str, description: str, reward: str, is_completed: bool = False):
        self.title = title
        self.description = description
        self.reward = reward
        self.is_completed = is_completed

    def complete(self):
        self.is_completed = True
        return f"Задание '{self.title}' выполнено! Награда: {self.reward}"

    def __str__(self):
        status = "Выполнено" if self.is_completed else "Активно"
        return f"[{status}] {self.title}: {self.description}"


class Mita:
    """Базовый класс Миты"""

    def __init__(self, name: str, description: str, traits: list[Trait], quests: list[Quest]):
        self.name = name
        self.description = description
        self.traits = traits
        self.quests = quests
        self.is_active = True

    def add_trait(self, trait: Trait):
        self.traits.append(trait)

    def add_quest(self, quest: Quest):
        self.quests.append(quest)

    def get_active_quests(self):
        return [q for q in self.quests if not q.is_completed]

    def complete_quest(self, quest_title: str):
        for quest in self.quests:
            if quest.title == quest_title and not quest.is_completed:
                return quest.complete()
        return "Задание не найдено или уже выполнено"

    def __str__(self):
        traits_str = "\n".join(str(t) for t in self.traits)
        quests_str = "\n".join(str(q) for q in self.quests)
        return f"Мита: {self.name}\nОписание: {self.description}\n\nЧерты:\n{traits_str}\n\nЗадания:\n{quests_str}"


class Player:
    """Класс игрока"""

    def __init__(self, name: str, level: int = 1):
        self.name = name
        self.level = level
        self.completed_quests = []
        self.active_quests = []
        self.encountered_mitas = []

    def encounter_mita(self, mita: Mita):
        if mita not in self.encountered_mitas:
            self.encountered_mitas.append(mita)
            self.active_quests.extend(mita.get_active_quests())
            return f"Вы встретили новую Миту: {mita.name}"
        return f"Вы снова встретили Миту: {mita.name}"

    def complete_quest(self, quest_title: str):
        for quest in self.active_quests[:]:
            if quest.title == quest_title:
                result = quest.complete()
                self.completed_quests.append(quest)
                self.active_quests.remove(quest)
                self.level += 1
                return f"{result}\nУровень повышен до {self.level}!"
        return "Задание не найдено среди активных"

    def __str__(self):
        return f"Игрок: {self.name} (Уровень: {self.level})\nАктивные задания: {len(self.active_quests)}\nЗавершенные задания: {len(self.completed_quests)}"


class World:
    """Класс игрового мира"""

    def __init__(self):
        self.mitas = []
        self.players = []

    def add_mita(self, mita: Mita):
        self.mitas.append(mita)

    def add_player(self, player: Player):
        self.players.append(player)

    def get_mita_by_name(self, name: str):
        for mita in self.mitas:
            if mita.name == name:
                return mita
        return None

    def get_player_by_name(self, name: str):
        for player in self.players:
            if player.name == name:
                return player
        return None

    def __str__(self):
        return f"Игровой мир:\nМиты: {len(self.mitas)}\nИгроки: {len(self.players)}"


def main():
    # Создаем игровой мир
    world = World()

    # Создаем уникальные черты для Мит
    fire_trait = Trait("Огненная аура", "Мита окружена пламенем", "Наносит урон при приближении")
    healing_trait = Trait("Исцеляющий свет", "Мита излучает целебную энергию", "Восстанавливает здоровье")
    shadow_trait = Trait("Теневой шаг", "Мита может перемещаться через тени", "Может телепортироваться")

    # Создаем задания для Мит
    fire_quest1 = Quest("Пламя возмездия", "Найти и наказать предателя", "Огненный меч")
    fire_quest2 = Quest("Испытание жаром", "Пройти через огненный лабиринт", "Устойчивость к огню")

    healing_quest1 = Quest("Исцеление ран", "Помочь 10 раненым", "Благословение здоровья")
    shadow_quest1 = Quest("Теневой контракт", "Устранить цель скрытно", "Теневой плащ")

    # Создаем Миты
    fire_mita = Mita("Игнис", "Огненная Мита, хранитель пламени", [fire_trait], [fire_quest1, fire_quest2])
    healing_mita = Mita("Люмин", "Целительная Мита, дарующая жизнь", [healing_trait], [healing_quest1])
    shadow_mita = Mita("Умбрис", "Теневая Мита, мастер скрытности", [shadow_trait], [shadow_quest1])

    # Добавляем Миты в мир
    world.add_mita(fire_mita)
    world.add_mita(healing_mita)
    world.add_mita(shadow_mita)

    # Создаем игрока
    player = Player("Аэрин")
    world.add_player(player)

    # Демонстрация взаимодействий
    print("=== Игрок встречает Мит ===")
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
    print(world)

if __name__ == "__main__":
    main()