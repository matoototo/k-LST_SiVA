def tokenize_squad(dataset, tokenizer, max_length):
    # If we need to truncate, truncate the context instead of the question
    tokenized_inputs = tokenizer(
        dataset["question"],
        dataset["context"],
        max_length=max_length,
        truncation="only_second",
        return_offsets_mapping=True
    )

    offset_mapping = tokenized_inputs.pop("offset_mapping")
    start_positions = []
    end_positions = []

    # Update the start and end positions
    for i, offsets in enumerate(offset_mapping):
        answer = dataset["answers"][i]
        # Start/end character index of the answer in the text
        start_char = answer["answer_start"][0]
        end_char = start_char + len(answer["text"][0])

        sequence_ids = tokenized_inputs.sequence_ids(i)
        # String of 1s in sequence_ids[i] is the context, find first and last
        context_start = sequence_ids.index(1)
        context_end = len(sequence_ids) - 1 - sequence_ids[::-1].index(1)

        # If the answer is out of the span (in the question) or after the context, set to 0,0
        if end_char < offsets[context_start][0] or start_char > offsets[context_end][1]:
            start_positions.append(0)
            end_positions.append(0)
        else:
            idx = context_start

            while offsets[idx][0] <= start_char and idx < context_end:
                idx += 1
            start_positions.append(idx - 1)

            while idx >= context_start and offsets[idx][1] >= end_char:
                idx -= 1
            end_positions.append(idx + 1)

    tokenized_inputs["start_positions"] = start_positions
    tokenized_inputs["end_positions"] = end_positions

    return tokenized_inputs


def tokenize_sst2(dataset, tokenizer, max_length):
    tokenized_inputs = tokenizer(
        dataset["sentence"],
        max_length=max_length,
        truncation=True
    )

    return tokenized_inputs