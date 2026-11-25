#include <QCoreApplication>
#include <QTranslator>
#include <QFile>
#include <QJsonDocument>
#include <QJsonArray>
#include <QJsonObject>
#include <QTextStream>
#include <QString>

#include <cstdlib>
#include <vector>

int main(int argc, char* argv[])
{
    QCoreApplication app(argc, argv);
    QTextStream out(stdout);

    if (argc != 4)
        return EXIT_FAILURE;

    QTranslator previous;
    QTranslator filtered;

    if (!previous.load(
        QString::fromLocal8Bit(argv[1])
    ))
        return EXIT_FAILURE;

    if (!filtered.load(
        QString::fromLocal8Bit(argv[2])
    ))
        return EXIT_FAILURE;

    QFile input(QString::fromLocal8Bit(argv[3]));

    if (!input.open(QIODevice::ReadOnly))
        return EXIT_FAILURE;

    QJsonParseError error;

    const auto document =
        QJsonDocument::fromJson(input.readAll(), &error);

    if (
        error.error != QJsonParseError::NoError
        || !document.isArray()
    )
        return EXIT_FAILURE;

    const auto records = document.array();

    int preserved = 0;
    int fallback = 0;
    int assertions = 0;

    for (const auto& value : records) {

        const auto row = value.toObject();

        const auto context =
            row.value("context").toString().toUtf8();

        const auto source =
            row.value("source").toString().toUtf8();

        const auto comment =
            row.value("comment").toString().toUtf8();

        const auto action =
            row.value("action").toString();

        const char* disambiguation =
            comment.isEmpty()
            ? nullptr
            : comment.constData();

        const std::vector<int> numbers =
            row.value("numerus").toBool()
            ? std::vector<int>{0, 1, 2, 5, 11, 21, 100}
            : std::vector<int>{-1};

        for (int n : numbers) {

            if (action == "preserved") {

                const auto before = previous.translate(
                    context.constData(),
                    source.constData(),
                    disambiguation,
                    n
                );

                const auto after = filtered.translate(
                    context.constData(),
                    source.constData(),
                    disambiguation,
                    n
                );

                if (
                    before != after
                    || before.isNull() != after.isNull()
                ) {
                    out << "FAIL: retained translation changed: "
                        << context << " / " << source << "\n";

                    return EXIT_FAILURE;
                }

            } else if (action == "fallback") {

                const auto expected =
                    QCoreApplication::translate(
                        context.constData(),
                        source.constData(),
                        disambiguation,
                        n
                    );

                const bool installed =
                    app.installTranslator(&filtered);

                const auto actual =
                    QCoreApplication::translate(
                        context.constData(),
                        source.constData(),
                        disambiguation,
                        n
                    );

                if (installed)
                    app.removeTranslator(&filtered);

                if (actual != expected) {

                    out << "FAIL: stale translation fallback: "
                        << context << " / " << source << "\n";

                    return EXIT_FAILURE;
                }

            } else {

                return EXIT_FAILURE;
            }

            ++assertions;
        }

        if (action == "preserved")
            ++preserved;
        else
            ++fallback;
    }

    out << preserved << " "
        << fallback << " "
        << assertions << "\n";

    return EXIT_SUCCESS;
}
