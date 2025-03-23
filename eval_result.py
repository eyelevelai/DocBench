import argparse
import json



def calc_accuracy(res_dir):
    with open(res_dir, 'r') as f:
        new_res_list = [json.loads(line) for line in f]

    score1 = [res for res in new_res_list if "1" in res['eval'][:20]]
    micro_acc = len(score1) / len(new_res_list)

    types = {
        'text-only': 'text',
        'multimodal-f': 'mm',
        'multimodal-t': 'mm',
        'multimodal': 'mm',
        'meta-data': 'meta',
        'una': 'una'
    }

    file_ranges = {
        'aca': range(0, 49),
        'fin': range(49, 89),
        'gov': range(89, 133),
        'law': range(133, 179),
        'new': range(179, 229)
    }

    type_counts = {key: {'wr': 0, 'total': 0} for key in types.values()}
    file_counts = {key: {'cor': 0, 'total': 0} for key in file_ranges.keys()}

    for res in new_res_list:
        evalres = res['eval'][:20]
        res_type = types.get(res['type'], 'una')
        if "0" in evalres:
            type_counts[res_type]['wr'] += 1
        type_counts[res_type]['total'] += 1

        res_file = int(res['file'])
        for key, f_range in file_ranges.items():
            if res_file in f_range:
                if "1" in evalres:
                    file_counts[key]['cor'] += 1
                file_counts[key]['total'] += 1
                break

    type_acc = {key: 1 - val['wr'] / val['total'] if val['total'] > 0 else None for key, val in type_counts.items()}
    file_acc = {key: val['cor'] / val['total'] if val['total'] > 0 else None for key, val in file_counts.items()}

    print()
    for key, acc in file_acc.items():
        if acc is not None:
            print(f"{key.capitalize()} Accuracy: {acc * 100:.1f}%")

    for key, acc in type_acc.items():
        if acc is not None:
            print(f"{key.capitalize()} Accuracy: {acc * 100:.1f}%")

    print(f"\n===\nOverall Accuracy: {micro_acc * 100:.1f}%\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--system", type=str, default="", choices=['gpt-4o','gpt4', 'gpt4_pl', 'gpt-4o_pl', 'gpt3.5', 'phi3-medium','commandr-35b','internlm2-20b', 'internlm2-7b', 'chatglm3-6b','gpt3.5','llama3-8b','llama3-70b','yi1.5-9b', 'yi1.5-34b','mixtral-8x7b','mistral-7b','gemma-7b', 'llama2-13b', 'kimi', 'claude3','glm4', 'qwen2.5', 'ernie4', 'gx'], help="The name of evaluated system.")
    parser.add_argument("--result_dir", type=str, default=".",
                        help="Folder to save results.")


    args = parser.parse_args()

    eval_system = args.system
    result_dir = args.result_dir

    calc_accuracy(f"{result_dir}/{eval_system}_eval_output.jsonl")



if __name__ == "__main__":
    main()