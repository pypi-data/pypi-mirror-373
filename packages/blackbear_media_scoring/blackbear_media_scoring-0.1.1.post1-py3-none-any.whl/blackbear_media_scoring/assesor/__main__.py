import argparse
import json

from dotenv import load_dotenv

from blackbear_media_scoring.assesor.assess import Assessor


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Assess text for sensitive content.")
    parser.add_argument("text", help="The text content to be scored.")
    parser.add_argument(
        "--model",
        default="gemini",
        help="The LLM model to use for assessment. Supported models: gemini, openrouter (default: gemini)",
    )
    args = parser.parse_args()

    try:
        assessor = Assessor(model=args.model)
        score_result = assessor.score_text(args.text)
        result = {"status": "success", **score_result.to_dict()}
        print(json.dumps(result))
    except ValueError as e:
        result = {"status": "error", "message": f"Error: {e}"}
        print(json.dumps(result))
    except Exception as e:
        result = {"status": "error", "message": f"An unexpected error occurred: {e}"}
        print(json.dumps(result))


if __name__ == "__main__":
    main()
