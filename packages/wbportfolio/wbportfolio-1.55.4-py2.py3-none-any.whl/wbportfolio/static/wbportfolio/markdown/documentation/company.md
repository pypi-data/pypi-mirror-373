# Companies
A list of every company saved in the database.

## Columns:
Each column title has three lines on the right if you hover over it. Click on them to show options for that column. The second tab of the options menu will allow you to filter the column, the third to completely hide entire columns. Click on anywhere else on the column to order it, cycling between ascending, descending and no ordering. Hold shift while clicking to order multiple columns with individual weights.

### Name:
The name of the company.

### City:
The city of the company's primary address. Hover over the name to display the full address.

### Type:
The company's type. Company types can be added, edited and deleted by managers under CRM > Administration > Company Types.

### Tier:
The company's tier. Tiers range from 1 to 5 and are automatically computed like this:
_Company is of status client or TPM:_
| Invested AUM / AUM  | Tier |
| -------- | --------|
| > 0.1 | Tier 1 |
| 0.05 - 0.1 | Tier 2 |
| 0.02 - 0.05 | Tier 3 |
| 0.01 - 0.02 | Tier 4 |
| default | Tier 5 |

_Company is *not* of status client or TPM:_
| AUM  | Tier |
| -------- | --------|
| > 10,000,000,000 $ | Tier 1 |
| 5,000,000,000 \$ - 10,000,000,000 $ | Tier 2 |
| 1,000,000,000 \$ - 5,000,000,000 $ | Tier 3 |
| 500,000,000 \$ - 1,000,000,000 $ | Tier 4 |
| default | Tier 5 |

### Status:
The company's status. Company statuses can be added, edited and deleted by managers under CRM > Administration > Customer Status.

### AUM Invested:
The company's assets under management managed by the main company.

### AUM:
Total assets under management for the company.

### Potential:
The potential reflects how much potential a company (regardless if client/propective) has. Formula: AUM * (Asset Allocation * Asset Allocation Max Investment) - Invested AUM. The field is populated automatically.

### Primary Relationship Manager:
The primary relationship manager of this company. Hover over the name to display further information about the person.

### Last Activity:
The name and end date of the company's last activity. Hover over it to display further information about the activity. Column can also be ordered by end date of the activity.

### Activity Heat:
A visual representation of the company's activeness. The data representation ranges from 0 to 1 which needs to be kept in mind to be able to apply a proper filter to the column.

## Filters:

### No Activity:
Filter companies with no activity for x amount of time.

### Companies' Employee:
Display employers of the selected person.

## Search Field:
Typing in the search field allows to filter the companies by name.

## Buttons:
You can right-click each row to reveal three buttons:

### Activities:
Displays activities for the row's company.

### Employees:
Displays a list of the company's employees.

### Relationship Managers:
Displays all relationship managers of the row's company.
