from typing import Dict, Any
import json

q1 = {
    "question_number": 1,
      "question": "What is the largest mammal in the world?", "answers": ["Elephant", "Blue Whale", "Giraffe", "Hippopotamus"],
      "correct_answer": "Blue Whale",
      "explanation": "The blue whale is the largest mammal and the largest animal known to have ever existed."
}

q2 = {
    "question_number": 2,
    "question": "Which animal is known as the 'King of the Jungle'?",
    "answers": ["Tiger", "Elephant", "Lion", "Gorilla"],
    "correct_answer": "Lion",
    "explanation": "The lion is traditionally known as the 'King of the Jungle' due to its majestic appearance and position as a top predator."
}

q3 = {
    "question_number": 3,
    "question": "Which animal is famous for its distinctive black and white stripes?",
    "answers": ["Zebra", "Panda", "Skunk", "Orca"],
    "correct_answer": "Zebra",
    "explanation": "Zebras are well-known for their unique black and white stripes, which help them blend into their environment and confuse predators."
}

q4 = {
    "question_number": 4,
    "question": "What is the fastest land animal in the world?",
    "answers": ["Cheetah", "Pronghorn", "Antelope", "Lion"],
    "correct_answer": "Cheetah",
    "explanation": "The cheetah is recognized as the fastest land animal, capable of reaching speeds up to 70 mph in short bursts."
}

q5 = {
    "question_number": 5,
    "question": "Which sea animal is known for having eight arms?",
    "answers": ["Squid", "Octopus", "Jellyfish", "Starfish"],
    "correct_answer": "Octopus",
    "explanation": "Octopuses are marine animals with eight arms, which they use for locomotion and capturing prey."
}

q6 = {
    "question_number": 6,
    "question": "Which is the largest species of shark?",
    "answers": ["Great White Shark", "Hammerhead Shark", "Whale Shark", "Tiger Shark"],
    "correct_answer": "Whale Shark",
    "explanation": "The whale shark is the largest species of shark and is known for its gentle nature despite its size."
}

q7 = {
    "question_number": 7,
    "question": "Which marine mammal is celebrated for its intelligence and playful behavior?",
    "answers": ["Seal", "Walrus", "Dolphin", "Manatee"], "correct_answer": "Dolphin",
    "explanation": "Dolphins are known for their high intelligence, playful behavior, and complex social interactions."
}

q8 = {
    "question_number": 8,
    "question": "Which animal is renowned for its long neck?",
    "answers": ["Camel", "Giraffe", "Ostrich", "Kangaroo"],
    "correct_answer": "Giraffe",
    "explanation": "Giraffes are famous for their long necks, which help them reach leaves high up in trees."
}

q9 = {
    "question_number": 9,
    "question": "Which animal is known for carrying its home on its back?",
    "answers": ["Snail", "Turtle", "Crab", "Hermit Crab"],
    "correct_answer": "Turtle",
    "explanation": "Turtles are known for carrying their shells, which serve as both their home and protection from predators."
}

q10 = {
    "question_number": 10,
    "question": "Which animal is often referred to as the 'Ship of the Desert'?",
    "answers": ["Llama", "Camel", "Horse", "Donkey"],
    "correct_answer": "Camel",
    "explanation": "Camels are known as the 'Ship of the Desert' due to their ability to travel long distances across arid landscapes."
}

q11 = {
    "question_number": 11,
    "question": "Which sea animal is known for its ability to change colors to blend with its surroundings?",
    "answers": ["Cuttlefish", "Starfish", "Seahorse", "Crab"],
    "correct_answer": "Cuttlefish",
    "explanation": "Cuttlefish can change their skin color and texture rapidly, which helps them camouflage in various environments."
}

q12 = {
    "question_number": 12,
    "question": "Which bird is known for its beautiful tail display and vibrant colors?",
    "answers": ["Peacock", "Parrot", "Flamingo", "Macaw"],
    "correct_answer": "Peacock",
    "explanation": "Peacocks are celebrated for their spectacular tail feathers, which they fan out to attract mates."
}

q13 = {
    "question_number": 13,
    "question": "What is the largest land carnivore?",
    "answers": ["Grizzly Bear", "Polar Bear", "Lion", "Tiger"],
    "correct_answer": "Polar Bear",
    "explanation": "Polar bears are the largest land carnivores, primarily found in the Arctic region and known for their powerful build."
}

q14 = {
    "question_number": 14,
    "question": "Which sea animal is often called the 'Unicorn of the Sea' because of its long, spiraled tusk?",
    "answers": ["Beluga Whale", "Narwhal", "Manta Ray", "Sea Lion"],
    "correct_answer": "Narwhal",
    "explanation": "Narwhals are sometimes referred to as the 'Unicorn of the Sea' due to the prominent tusk that protrudes from their head."
}

q15 = {
    "question_number": 15,
    "question": "Which amphibian is known for its vibrant colors and toxicity?",
    "answers": ["Salamander", "Toad", "Poison Dart Frog", "Newt"],
    "correct_answer": "Poison Dart Frog",
    "explanation": "Poison dart frogs are noted for their bright coloration and potent skin toxins, serving as a warning to potential predators."
}

q_bank = [q1, q2, q3, q4, q5,
          q6, q7, q8, q9, q10,
          q11, q12, q13, q14, q15]
# generate some sample questions

'''
{
    "question": "What has the World Health Organization classified nighttime shift work as?",
    "distractors": ["A necessary career choice", "An essential job role", "A common lifestyle", "An unavoidable health risk"],
    "correct_answer": "A probable carcinogen",
    "explanation": "The World Health Organization has classified nighttime shift work as a 'probable carcinogen' due to its links with cancer development, particularly because it disrupts sleep and circadian rhythms."
}
'''
def verify_dict(content: str) -> Dict[str, Any]:
    """
    Verify if the quiz is a valid JSON string.
    """
    # Try to find JSON content if there's text around it
    if content.find('{') > -1 and content.rfind('}') > -1:
        start = content.find('{')
        end = content.rfind('}') + 1
        content = content[start:end]

    try:
        quiz_dict = json.loads(content)
        required_keys = ['question', 'distractors', 'correct_answer', 'explanation']
        # Check if all required keys are present
        for key in required_keys:
            if key not in quiz_dict:
                raise ValueError(f"Missing required key: {key}")

        if isinstance(quiz_dict, dict):
            return quiz_dict
        else:
            raise ValueError("Invalid JSON format")

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return {
                "question": "Error generating quiz question",
                "distractors": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A",
                "explanation": f"Error: {str(e)}. Raw response: {content[:100]}..."
            }
    except Exception as e:
        print(f"Error: {e}")
        return {
                "question": "Error generating quiz question",
                "answers": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A",
                "explanation": f"Error: {str(e)}. Raw response: {content[:100]}..."
            }


def format_quiz(quiz: str) -> dict[str, Any]:
    """
    Format the quiz into a more reliable format.
    """
    formatted_quiz = {}
    quiz_dict = verify_dict(quiz)
    try:
        formatted_quiz['question'] = quiz_dict['question']

        formatted_quiz['answers'] = quiz_dict['distractors']
        # sometimes, LLM messes up and the correct answer is already in the distractors
        if quiz_dict['correct_answer'] not in formatted_quiz['answers']:
            formatted_quiz['answers'].append(quiz_dict['correct_answer']) # is a list

        # Shuffle the answers
        import random
        random.shuffle(formatted_quiz['answers'])

        formatted_quiz['correct_answer'] = quiz_dict['correct_answer']
        formatted_quiz['explanation'] = quiz_dict['explanation']
    except Exception as e:
        print(f"Error formatting quiz: {e}")
        formatted_quiz = {}

    return formatted_quiz