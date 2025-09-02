# krishnautoml/cli.py

import argparse
from krishnautoml import KrishnAutoML


def main():
    parser = argparse.ArgumentParser(
        prog="krishnautoml", description="KrishnAutoML CLI"
    )
    parser.add_argument("command", choices=["fit"], help="Command to run")
    parser.add_argument("--data", type=str, required=True, help="Path to CSV file")
    parser.add_argument("--target", type=str, required=True, help="Target column")
    parser.add_argument("--report", action="store_true", help="Generate HTML report")
    parser.add_argument(
        "--save", type=str, default="best_model.pkl", help="Save best model to file"
    )

    args = parser.parse_args()

    if args.command == "fit":
        automl = KrishnAutoML(target=args.target, problem_type="auto")
        automl.load_data(args.data).preprocess().train_models()

        metrics = automl.evaluate()
        automl.save(args.save)

        print("\nTraining complete!")
        print("Best model saved to:", args.save)
        print("Metrics:", metrics)

        if args.report:
            from krishnautoml.reporting.report_generator import ReportGenerator

            reporter = ReportGenerator()
            report_path = reporter.generate_report(
                project_name="KrishnAutoML_Run",
                metrics=metrics,
                model_info={"name": str(type(automl.best_model).__name__)},
            )
            print("Report generated at:", report_path)
