# Copyright © 2024 Apple Inc.

from mlx_lm import generate, load


def test_llm_generate_stream(model_path):
    # Load the corresponding model and tokenizer
    model, tokenizer = load(path_or_hf_repo=model_path)

    # Conversation history to maintain context
    conversation = []

    # Specify the maximum number of tokens
    max_tokens = 1_000

    # Specify if tokens and timing information will be printed
    verbose = True

    print("Multi-round conversation started. Type 'quit' or 'exit' to end.")
    print("=" * 50)

    while True:
        # Get user input
        user_input = input("\nUser: ").strip()

        # Check for exit commands
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        if not user_input:
            continue

        # Add user input to conversation history
        conversation.append({"role": "user", "content": user_input})

        # Transform the conversation into the chat template
        prompt = tokenizer.apply_chat_template(
            conversation=conversation, add_generation_prompt=True
        )

        # Generate response
        print("Assistant: ", end="", flush=True)

        # Generate text, already handled KV cache
        response = generate(
            model=model,
            tokenizer=tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            verbose=verbose,
        )

        # Extract the generated text (response includes the prompt)
        generated_text = response.strip()

        # Add assistant response to conversation history
        conversation.append({"role": "assistant", "content": generated_text})

        print()  # New line after response


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, default="mlx-community/Qwen3-1.7B-4bit-DWQ")
    args = parser.parse_args()
    test_llm_generate_stream(args.model_path)
