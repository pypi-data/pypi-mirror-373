# NotificationList

## What NotificationList Does

NotificationList is a Python package designed for efficiently consolidating breach response notification lists. It simplifies the process of managing and generating unique identifiers for affected parties based on their names, making it an essential tool for data management in security and compliance workflows.

## Key Features

- **Efficient Consolidation**: Easily merge and manage breach notification contacts.
- **Unique ID Generation**: Automatically generate unique identifiers based on first, middle, and last names.
- **User-Friendly API**: Simple methods for quick integration into your projects.

## How to Install NotificationList

To install this package, run:

```bash
pip install NotificationList
```

## Get Started Using NotificationList

### Quick Code Demo

Here's a quick example to demonstrate how to use the package after installation:

```python
import NotificationList as nl

# Display help information
nl.help()
```

Output:
```
You will get contact information.
```

### Ensure the Raw Data has the expected column names

required_columns = ['FIRST NAME', 'LAST NAME', 'MIDDLE NAME']

### Generating Unique IDs

You can generate unique IDs based on contact names with the following method:

```python
import NotificationList as nl

# Generate unique IDs from a CSV file
nl.initial_unqid("Raw File.csv")
```

Output:
```
Basis on First Name, Middle Name & Last Name UNIQUE IDs are generated for initial merging.
```


<!-- ### Example Usage

Here’s a more detailed example demonstrating the functionality:

```python
# Load your contacts from a CSV file
contacts = nl.load_contacts("contacts.csv")

# Generate unique IDs for each contact
unique_ids = nl.generate_unique_ids(contacts)

# Print the unique IDs
print(unique_ids)
``` -->

## Maintainer

- [Ranjeet Aloriya](https://www.linkedin.com/in/ranjeet-aloriya/)

<!-- ## Community

Join our community to discuss features, share your projects, or seek help:

- GitHub Discussions: [Link to Discussions]
- Stack Overflow: [Link to relevant tags] -->

## How to Cite NotificationList

If you use NotificationList in your research or projects, please cite it as follows:

```
Your Name, Collaborator's Name. (Year). NotificationList: A Python Package for Breach Response Notifications. GitHub. URL
```

<!-- ## Contribution Guidelines

We welcome contributions to NotificationList! Please follow these guidelines:

1. **Fork the repository**: Create your own fork of the project.
2. **Create a feature branch**: Make a new branch for your feature or bug fix.
3. **Make your changes**: Implement your changes in your branch.
4. **Submit a pull request**: Once you’re ready, submit a pull request for review.

For detailed contribution instructions, check the [CONTRIBUTING.md](link-to-contributing-file). -->

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) for more details.

---

Thank you for using NotificationList! We hope it simplifies your breach response efforts.