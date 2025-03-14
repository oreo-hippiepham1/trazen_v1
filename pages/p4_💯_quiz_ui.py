from ninja import expand
from requests import session
import streamlit as st

from utils import *
from rag import *

import time
import random


## SOURCE: https://medium.com/@fesomade.alli/building-a-quiz-app-in-python-using-streamlit-d7c1aab4d690

st.set_page_config(
    page_title="Quiz UI",
    page_icon="💯",
    layout="centered",
)

def nl(num_of_lines):
    """
    Generates some newlines
    """
    for i in range(num_of_lines):
        st.write(" ")

class StateManager:
    """Centralized session state management"""
    @staticmethod
    def initialize_states():
        ss = st.session_state

        # Default configuration values
        DEFAULT_CONFIG = {
            'n_quiz': 5,  # matches slider default
            'difficulty': 1,  # matches difficulty slider default
            'topic': "Animals",  # matches selectbox default
            'n_distractors': 3,  # matches distractor slider default
            'hints': False  # matches checkbox default
        }

        # Quiz UI states
        if 'counter' not in ss:
            ss['counter'] = 0
        if 'start' not in ss:
            ss['start'] = False
        if 'stop' not in ss:
            ss['stop'] = False
        if 'refresh' not in ss:
            ss['refresh'] = False
        if 'button_label' not in ss:
            ss['button_label'] = ['GENERATE QUIZZES', 'SUBMIT ANSWERS', 'RELOAD']
        if 'current_quiz' not in ss:
            ss['current_quiz'] = []
        if 'user_answers' not in ss:
            ss['user_answers'] = []

        # Quiz Config states - initialize with defaults
        if 'n_quiz' not in ss:
            ss['n_quiz'] = DEFAULT_CONFIG['n_quiz']
        if 'difficulty' not in ss:
            ss['difficulty'] = DEFAULT_CONFIG['difficulty']
        if 'topic' not in ss:
            ss['topic'] = DEFAULT_CONFIG['topic']
        if 'n_distractors' not in ss:
            ss['n_distractors'] = DEFAULT_CONFIG['n_distractors']
        if 'hints' not in ss:
            ss['hints'] = DEFAULT_CONFIG['hints']
        if 'conf_save' not in ss:
            ss['conf_save'] = True  # Start with saved state

        # Initialize current_config with defaults if not exists
        if 'current_config' not in ss:
            ss['current_config'] = DEFAULT_CONFIG.copy()

st.title("Test Quiz UI 💯")

# Initialize all session states at startup
StateManager.initialize_states()

# Set tabs
tab1, tab2= st.tabs(["Quiz", "Configs"])

class QuizUITest():
    def __init__(self, quiz_configs):
        # Update n_quiz from configs
        # st.session_state['n_quiz'] = quiz_configs['n_quiz']
        pass

    def load_quiz(self):
        ss = st.session_state
        q_bank = st.session_state['quiz_bank']  # quiz bank is a list of dicts
        if ss['current_config']['n_quiz'] <= len(q_bank):
            ss['current_quiz'] = random.sample(q_bank, ss['current_config']['n_quiz']) # randomize quiz questions
        else:
            ss['current_quiz'] = q_bank # if not enough questions, use all available

    def _reset(self):
        ss = st.session_state
        ss['current_quiz'] = []
        ss['user_answers'] = []
        ss['counter'] = 0
        ss['start'] = False
        ss['stop'] = False
        ss['refresh'] = False

    def btn_click(self):
        ss = st.session_state

        ss.counter += 1 # adds 1 upon click
        if ss.counter > 2: # reload
            ss.counter = 0
            self._reset()

        else: # either start or submit
            self.update_ss()
            with st.spinner("Loading..."):
                time.sleep(2) # simulates loading time + avoids spamming

    def update_ss(self):
        ss = st.session_state
        if ss.counter == 1: # start quiz
            ss.start = True
            self.load_quiz()
            ss.stop = False
        elif ss.counter == 2: # submit quiz
            ss.stop = True
            ss.start = False
            ss.refresh = True


    def main(self):
        ss = st.session_state

        with st.container():
            for quiz_idx, quiz in enumerate(ss.current_quiz):
                q_num_placeholder = st.empty()
                q_placeholder = st.empty()
                answers_placeholder = st.empty()
                results_placeholder = st.empty()
                expander_area_explanation = st.empty()
                expander_area_reference = st.empty()

                #current_question = i + 1
                # Display question number
                q_num_placeholder.write(f"**Question {quiz_idx+1}**")
                # Display question content
                q_placeholder.write(f"*{quiz['quiz_formatted'].get('question')}*") # current_quiz is list[dict]
                # Display question options (answers)
                answers = quiz['quiz_formatted'].get('answers')
                answers_placeholder.radio(
                    "",
                    answers,
                    index=1,
                    key=f"Q{quiz_idx+1}" # binds current answer choice to session_state
                )
                nl(2)

                # Grade answer + Show correct
                if ss.stop:
                    # length of user answers
                    if len(ss.user_answers) < len(ss.current_quiz):
                        # compare answers
                        if (quiz['quiz_formatted'].get('correct_answer') == ss[f'Q{quiz_idx+1}']):
                            ss.user_answers.append(1)
                        else:
                            ss.user_answers.append(0)
                    else:
                        pass

                    # Feedback
                    if ss.user_answers[quiz_idx] == 1:
                        results_placeholder.success("Correct")
                    else:
                        results_placeholder.error("Incorrect")

                    # Explanations
                    with expander_area_explanation.expander(label="Explanation", expanded=False):
                        st.write(quiz['quiz_formatted'].get('explanation'))

                    # References
                    with expander_area_reference.expander(label="References", expanded=False):
                        docs = quiz['quiz_src']  # Dict[str, List]

                        for ref_idx, (source, content) in enumerate(zip(docs['source'], docs['content'])):
                            page = source['page']
                            chapter = source['chapter_title']

                            reference = f"Chapter: {chapter}, Page: {page}"
                            with st.popover(label=f"Reference {ref_idx+1} - {reference}"):
                                st.caption(content)


        # Final score
        if ss.stop:
            st.write(f"Your score is {sum(ss.user_answers)}/{len(ss.user_answers)}")
            st.button(
                label=ss['button_label'][ss.counter],
                key='btn_press',
                on_click=self.btn_click,
                help="Click to start the quiz, submit your answers, or reload the quiz."
            )
            st.stop()

        # Quiz button
        st.button(
            label=ss['button_label'][ss.counter],
            key='btn_press',
            on_click=self.btn_click,
            help="Click to start the quiz, submit your answers, or reload the quiz."
        )


class QuizConfigs():
    def __init__(self):
        pass  # State initialization is now handled by StateManager

    def get_configs(self):
        return st.session_state['current_config']

    def choice_selected(self):
        """Called when any config widget value changes"""
        ss = st.session_state
        if ss['conf_save']:  # Only mark as unsaved if it was previously saved
            ss['conf_save'] = False

    def _config_save(self):
        """Save current widget values to current_config"""
        ss = st.session_state

        # Validate values before saving
        if ss['n_quiz'] < 1:
            st.error("Number of quizzes must be at least 1")
            return

        if not ss['conf_save']:  # only save if there are unsaved changes
            # Create new config dict with current widget values
            new_config = {
                'n_quiz': ss['n_quiz'],
                'difficulty': ss['difficulty'],
                'n_distractors': ss['n_distractors'],
                'topic': ss['topic'],
                'hints': ss['hints']
            }

            # Update current_config with new values
            ss['current_config'].update(new_config)
            ss['conf_save'] = True
            st.success("Configuration saved successfully!")

    def main(self):
        ss = st.session_state

        # Display current active configuration
        st.subheader("Current Active Configuration")
        st.json(ss['current_config'])
        nl(2)

        st.subheader("Configuration Settings")
        n_quiz_slider = st.slider(
            label="**Number of Quizzes**",
            min_value=1,
            max_value=10,
            value=ss['current_config']['n_quiz'],  # Use current_config as default
            key='n_quiz',
            on_change=self.choice_selected
        )

        c1, c2 = st.columns(2)
        difficulty_slider = c1.slider(
            label="**Difficulty Level**",
            min_value=1,
            max_value=3,
            value=ss['current_config']['difficulty'],  # Use current_config as default
            key='difficulty',
            on_change=self.choice_selected
        )
        n_distractors_slider = c2.slider(
            label="**Number of Distractors**",
            min_value=0,
            max_value=3,
            value=ss['current_config']['n_distractors'],  # Use current_config as default
            key='n_distractors',
            on_change=self.choice_selected
        )

        topic = st.selectbox(
            label="**Topic**",
            options=["Animals", "Plants", "Minerals"],
            index=["Animals", "Plants", "Minerals"].index(ss['current_config']['topic']),  # Use current_config as default
            key='topic',
            on_change=self.choice_selected
        )

        hints = st.checkbox(
            label="**Show Hints**",
            value=ss['current_config']['hints'],  # Use current_config as default
            key='hints',
            on_change=self.choice_selected
        )

        if not ss['conf_save']:
            st.warning("You have unsaved changes!")

        save_btn = st.button(
            label='Save Configuration',
            key='save_btn',
            on_click=self._config_save,
            type="primary"  # Make it more prominent
        )


if __name__ == "__main__":
    quiz_conf = QuizConfigs()
    if ('selected_chapter' not in st.session_state) or ('selected_chapter_chunks' not in st.session_state):
        st.warning("Please select a chapter first! (Page 1) (not init)" )
        st.stop()

    if (st.session_state['selected_chapter'] is None) or(st.session_state['selected_chapter_chunks'] is None):
        st.warning("Please select a chapter first! (Page 1) (currently None)" )
        st.stop()

    with st.sidebar:
        st.write("Selected Chapter:")
        st.json(st.session_state['selected_chapter'])  # Display selected chapter info


    with tab1:
        # Initialize quiz bank if not already done
        if 'quiz_bank' not in st.session_state or st.session_state['quiz_bank'] is None:
            st.session_state['quiz_bank'] = None
            st.warning("Quiz bank is empty. Please generate it in the Page 3 (quiz gen). 👈")
        else:
            quiz_ui = QuizUITest(quiz_conf.get_configs())
            quiz_ui.main()

    with tab2:
        quiz_conf.main()
