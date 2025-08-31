# flake8: noqa
DK_KITCHEN_MERGE_TEMPLATE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type"
        content="text/html; charset=utf-8"/>
    <meta name="viewport"
        content="width=device-width, initial-scale=1.0"/>
    <title>DataKitchen Merge</title>
    <style type="text/css">
        body {
            margin: 0;
            padding: 0;
            background: #eeeeee !important;
        }

        h1, p {
            margin: 0;
        }

        .background {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            background-color: #eeeeee;
        }

        .content {
            margin: 0 auto;
            background-color: white;
            font-family: 'Roboto', 'Helvetica Neue', sans-serif;
            font-size: 14px;
            line-height: 20px;
            color: rgba(0, 0, 0, 0.87);
            width: 100%;
            min-width: 500px;
            max-width: 800px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 1px rgba(0, 0, 0, 0.14), 0 2px 1px rgba(0, 0, 0, 0.02);
        }

        .header {
            width: 100%;
            margin: 20px 32px 0;
        }

        .logo {
            width: 124px;
            vertical-align: top;
            padding-top: 4px;
            padding-left: 0;
        }

        .logo--full {
            height: 24px;
        }

        .logo--icon {
            height: 40px;
            display: none;
        }

        .title {
            font-size: 20px;
            line-height: 23px;
            white-space: nowrap;
            text-align: center;
            margin-bottom: 4px;
            padding-right: 124px;
            color: rgba(0, 0, 0, 0.87);
        }

        .title__status {
            color: #FF9800;
            font-size: 28px;
            line-height: 20px;
            vertical-align: middle;
            font-family: Arial sans-serif;
        }

        .title__status--Started {
            color: #1976D2;
        }

        .title__status--Completed {
            color: #4CAF50;
        }

        .title__status--Failed {
            color: #F44336;
        }

        .summary {
            padding: 4px 16px 16px;
            border: 1px solid rgba(0, 0, 0, 0.12);
            border-radius: 4px;
            margin: 8px 32px 4px;
        }

        .summary--statistics {
            margin-top: 0;
            margin-bottom: 20px;
        }

        .summary__title {
            height: 28px;
        }

        .summary__label {
            line-height: 16px;
            color: rgba(0, 0, 0, 0.54);
            width: 100px;
            height: 20px;
        }

        /* Unset link styles added by some clients */
        .summary__email a {
            color: rgba(0, 0, 0, 0.87) !important;
            text-decoration: none !important;
        }

        .link {
            color: #1976D2 !important;
            cursor: pointer !important;
            text-decoration: none;
        }

        .link--border {
            border-bottom: 1px solid #1976d2;
        }

        .link--margin {
            margin-right: 10px;
        }

        .section__title {
            margin: 0 32px;
            font-family: 'Roboto', 'Helvetica Neue', sans-serif;
            font-size: 20px;
            line-height: 23px;
        }

        .section__title__mso {
            margin-top: 8px;
            font-family: 'Roboto', 'Helvetica Neue', sans-serif;
            font-size: 20px;
            line-height: 23px;
        }

        .section__subtitle__container {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .section__subtitle {
            padding: 12px;
            font-family: 'Roboto', 'Helvetica Neue', sans-serif;
            font-size: 14px;
            line-height: 23px;
        }

        .section__content__container {
            margin: 0px 32px;
        }

        .section__content {
            font-family: 'Roboto', 'Helvetica Neue', sans-serif;
            font-size: 12px;
            line-height: 20px;
            border: 1px solid rgba(0, 0, 0, 0.12);
            border-radius: 4px;
            max-width: 100%;
            margin-top: 8px;
            width: 100%;
        }

        .section__content table {
            width: 100%;
            margin-bottom: 8px;
            margin-top: 8px;
            table-layout: fixed;
        }

        .section__content th,
        .section__content td {
            height: 14px;
            padding: 0 8px;
            color: rgba(0, 0, 0, 0.54);
        }

        .section__content th {
            font-weight: 400;
            text-align: left;
        }

        .section__content tr, th, tbody, thead {
            width: 100%;
        }

        .section__content td {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 150px;
        }

        .small-column {
            width: 5%;
        }

        .medium-column {
            width: 20%;
        }

        .big-column {
            width: 50%;
        }

        .section__content .section__number {
            padding-left: 12px;
        }

        .section__content .section__dark {
            color: rgba(0, 0, 0, 0.87);
        }

        .section__content .section__empty {
            height: 100px;
            text-align: center;
        }

        .section__content .test__status--Failed {
            color: #F44336;
        }

        .section__content .test__status--Warning {
            color: #FF9800;
        }

        .section__content .test__status--Passed {
            color: #06A04A;
        }

        .section__content .test__status--Log {
            color: #673AB7;
        }

        .section__link {
            padding: 0 32px;
        }

        .divider {
            border: none;
            background-color: rgba(0, 0, 0, 0.12);
            height: 1px;
            margin: 20px 0 24px;
        }

        .footer {
            color: rgba(0, 0, 0, 0.38);
            font-size: 12px;
        }

        .footer td {
            height: 52px;
            background-color: #FAFAFA;
            padding: 0 24px;
        }

        .footer a {
            color: rgba(0, 0, 0, 0.38) !important;
            border-bottom: 1px solid rgba(0, 0, 0, 0.38);
            text-decoration: none;
        }

        .footer__padding {
            height: 32px;
        }

        .align-right {
            text-align: right;
        }

        @media screen and (max-width: 600px) {
            .background__cell {
                padding: 0;
            }

            .content {
                border-width: 16px 16px 8px;
                font-size: 16px;
            }

            .logo {
                width: 44px;
                padding-top: 5px;
            }

            .logo--full {
                display: none;
            }

            .logo--icon {
                display: block;
            }
        }

        /* Remove space around the email design. */
        html,
        body {
            margin: 0 auto !important;
            padding: 0 !important;
            height: 100% !important;
            width: 100% !important;
        }

        /* Stop Outlook resizing small text. */
        * {
            -ms-text-size-adjust: 100%;
        }

        /* Stop Outlook from adding extra spacing to tables. */
        table,
        td {
            mso-table-lspace: 0pt !important;
            mso-table-rspace: 0pt !important;
        }

        /* Use a better rendering method when resizing images in Outlook IE. */
        img {
            -ms-interpolation-mode: bicubic;
        }
    </style>
</head>
<body>

<!-- BACKGROUND -->
<table role="presentation"
    cellpadding="32"
    cellspacing="0"
    border="0"
    class="background">
    <tr>
        <td class="background__cell">
            <!-- CONTENT -->
            <table role="presentation"
                cellpadding="2"
                cellspacing="0"
                border="0"
                class="content">
                <!-- HEADER -->
                <tr>
                    <td>
                        <table role="presentation"
                            cellpadding="2"
                            cellspacing="0"
                            border="0"
                            class="header">
                            <tr>
                                <!-- LOGO -->
                                <td class="logo">
                                    <!-- for regular screens -->
                                    <img src="https://dk-support-external.s3.amazonaws.com/support/dk_logo_horizontal.png"
                                        alt="DataKitchen Logo"
                                        height="24"
                                        class="logo--full">

                                    <!-- for smaller screens -->
                                    <!--[if !mso]><!-->
                                    <img src="https://dk-support-external.s3.amazonaws.com/support/dk_logo.png"
                                        alt="DataKitchen Logo"
                                        height="40"
                                        class="logo--icon">
                                    <!--<![endif]-->
                                </td>
                                <!-- TITLE -->
                                <td class="title">
                                    DataKitchen Merge
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td style="white-space: nowrap">
                        <!-- SUMMARY -->
                        <div class="summary">
                            <table
                                role="presentation"
                                cellpadding="2"
                                cellspacing="0"
                                border="0">
                                {% if error %}
                                <tr>
                                    <td colspan="2"
                                        class="summary__title">The kitchen merge failed with an error: {{ error.message }}.
                                    </td>
                                </tr>
                                {% else %}
                                <tr>
                                    <td colspan="2"
                                        class="summary__title"> The kitchen merge completed successfully.
                                    </td>
                                </tr>
                                {% endif %}

                                <tr>
                                    <td class="summary__label">Source Kitchen</td>
                                    <td>{{ from_kitchen_name }}</td>
                                </tr>
                                <tr>
                                    <td class="summary__label">Target Kitchen</td>
                                    <td>{{ to_kitchen_name }}</td>
                                </tr>
                            </table>
                        </div>
                    </td>
                </tr>

                <!-- FOOTER -->
                <tr>
                    <td colspan="2"
                        class="footer__padding"></td>
                </tr>
                <tr class="footer">
                    <td colspan="2"
                        align="right">
                        <a href="http://datakitchen.io"
                            target="_blank"
                            title="DataKitchen website">datakitchen.io</a>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>
</body>
</html>
"""
