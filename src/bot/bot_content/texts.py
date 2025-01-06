from dataclasses import dataclass
from src.bot.bot_content.basics import Commands, Modes


@dataclass
class VariousBotText:
    greeting: str
    all_commands: str
    cancel_all: str

    get_question: str
    ai_answer: str

    profile: str

    change_skill: str
    changed_skill: str

    change_mode: str
    changed_mode: str

    choose_one_or_cancel: str


actual_texts = VariousBotText(
    greeting='Привет, {user_id}! Я бот-интервьюер. Я могу задавать вопросы по программированию на Python. ',

    all_commands=f'— /{Commands.get_question_command}, чтобы получить вопрос собеседования.\n'
                 f'— /{Commands.change_mode_command}, чтобы выбрать, как ИИ будет задавать вопросы '
                 f'(все темы, конкретная тема, слабые темы).\n'
                 f'— /{Commands.change_skills_command}, чтобы выбрать конкретный навык, если хочешь подтянуть '
                 f'конкретную тему.\n'
                 f'— /{Commands.profile_command}, чтобы посмотреть карту навыков и режим тренировки.',

    cancel_all=f'Окей, отменяем.'
               f'\n\nЕсли захочешь продолжить, нажми:\n',

    get_question='Вопрос на тему: {skill}'
                 '\n\n{ai_question}',

    ai_answer='{ai_answer}\n\n'
              'Оценка навыка изменилась: {old_score} → {new_score}.',

    profile='👤 Карта навыков. Чем выше оценка у навыка, тем лучше.\n'
            '\n\n⚙️ {user_mode} — режим работы ИИ\n(all — все темы, specific — конкретная тема, '
            'worst — темы с самой низкой оценкой.'
            '\n\n💪 {user_skill} — навык для тренировки в режиме specific».',

    change_skill='Какую тему хочешь подтянуть?',

    changed_skill=f'Тема для тренировок  в режиме {Modes().specific} обновлена. '
                  'Теперь ИИ будет задавать вопросы по теме: «{skill}».'
                  f'\n\nНажми «{Commands.get_question_text}», чтобы ИИ сгенерировал новый вопрос.',

    choose_one_or_cancel=f"Выбери один из вариантов или нажми {Commands.cancel_text}",

    change_mode='По каким темам ИИ должен задавать вопросы:'
                '\n\n🔀 all — все темы в случайном порядке;'
                f'\n\n1️⃣ specific — конкретную тему (можно указать, выбрав «{Commands.change_skills_text}» в меню; '
                f'\n\n⬇️ worst — темы с самой низкой оценкой (можно посмотреть, выбрав «{Commands.profile_text}» в меню).',

    changed_mode='Режим тренировок обновлен на {current_mode}.'
)