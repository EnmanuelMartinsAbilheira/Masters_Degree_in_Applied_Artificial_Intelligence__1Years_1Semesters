# Load necessary libraries
library(readr)
library(tidyverse)
library(GGally)
library(ggplot2)
library(reshape2)
library(corrplot)
library(caret)

# Load data
data <- read.csv("D:/_MIAA/MEIA/csv/apple_quality.csv")

# --------------------------------------------------------
# Exploratory Data Analysis (EDA) with Visualizations
# --------------------------------------------------------

# Check for missing values
summary(data)

# Handle missing values in Acidity (assuming median imputation)
data$Acidity <- as.numeric(as.character(data$Acidity))
non_numeric <- is.na(data$Acidity_numeric) & !is.na(data$Acidity)
data$Acidity[is.na(data$Acidity)] <- median(data$Acidity, na.rm = TRUE)

# Check for missing values again (useful for further cleaning if needed)
summary(data)

# Visualizing Distributions of Individual Variables

# Histograms
# Using ggplot2
# Reset graphics state (optional)
ggplot.reset()
ggplot(data, aes(x = Size)) +
  geom_histogram(binwidth = 0.5, fill = "blue", color = "black") +
  theme_minimal() +
  labs(title = "Distribution of Size", x = "Size", y = "Count")


# Density plots
ggplot(data, aes(x = Sweetness)) +
  geom_density(fill = "green") +
  labs(title = "Density of Sweetness", x = "Sweetness")

# Visualizing Relationships Between Variables

# Scatter plots (example - Sweetness vs Crunchiness)
plot(data$Sweetness, data$Crunchiness, main = "Sweetness vs Crunchiness", xlab = "Sweetness", ylab = "Crunchiness")

# Pair Plots
ggpairs(data[, c("Size", "Weight", "Sweetness", "Crunchiness", "Juiciness", "Ripeness", "Acidity")])

# Correlation Matrix
cor_matrix <- cor(data[, sapply(data, is.numeric)])

# Heatmap with ggplot2
melted_cor_matrix <- melt(cor_matrix)
ggplot(melted_cor_matrix, aes(Var1, Var2, fill = value)) +
  geom_tile() +
  scale_fill_gradient2(midpoint = 0, low = "green", mid = "white", high = "red") +
  theme_minimal() +
  labs(title = "Correlation Matrix Heatmap")

# Categorical Variables
# Bar plot for Quality
quality_distribution <- table(data$Quality)
barplot(quality_distribution, main = "Distribution of Apple Quality", xlab = "Quality", ylab = "Count")

# --------------------------------------------------------
# Linear Regression Section
# --------------------------------------------------------

# Prepare Data for Linear Regression
regression_data <- data[, !(names(data) %in% c("A_id", "Quality"))]

# Fit the Linear Regression Model
model <- lm(Juiciness ~ ., data=regression_data)

# Display and interpret model summary
summary(model)

# Evaluate Model's Assumptions (plots not shown here)
par(mar = c(bottom = 2, left = 2, top = 2, right = 2))
#par(mfrow=c(2,2))
plot(model)

# Make Predictions (for demonstration)
predictions <- predict(model, regression_data)
head(predictions)
head(regression_data$Juiciness)

# --------------------------------------------------------
# Logistic Regression Section
# --------------------------------------------------------

# Prepare Data for Logistic Regression
data$QualityNumeric <- ifelse(data$Quality == "good", 1, 0)
logistic_data <- data[, c("Size", "Weight", "Sweetness", "Crunchiness", "Juiciness", "Ripeness", "Acidity", "QualityNumeric")]

# Fit the Logistic Regression Model
logistic_model <- glm(QualityNumeric ~ ., data = logistic_data, family = binomial)

# Display and interpret model summary
summary(logistic_model)

# Predicting outcomes using the model
fitted_results <- predict(logistic_model, newdata = logistic_data, type = "response")
predicted_class <- ifelse(fitted_results > 0.5, 1, 0)

# Now, ensure both actual and predicted are of the same length
actual <- logistic_data$QualityNumeric # Make sure this matches the data used in predict()
predicted <- as.factor(predicted_class)

# Check lengths (for troubleshooting)
print(length(actual))
print(length(predicted))

# Assuming the lengths match, create the confusion matrix
if (length(actual) == length(predicted)) {
  conf_matrix <- table(Predicted = predicted, Actual = actual)
  print(conf_matrix)
  
  # Calculate metrics based on the confusion matrix
  accuracy <- sum(diag(conf_matrix)) / sum(conf_matrix)
  print(paste("Accuracy:", accuracy))
  
  # Sensitivity and specificity calculations
  sensitivity <- conf_matrix["1", "1"] / sum(conf_matrix[, "1"])
  specificity <- conf_matrix["0", "0"] / sum(conf_matrix[, "0"])
  print(paste("Sensitivity:", sensitivity))
  print(paste("Specificity:", specificity))
} else {
  print("Error: Predicted and actual outcomes do not match in length.")
}


print(conf_matrix)

# Calculating accuracy, sensitivity, specificity, etc., from the confusion matrix
accuracy <- sum(diag(conf_matrix)) / sum(conf_matrix)
print(paste("Accuracy:", accuracy))

# Assuming '1' is the positive class and '0' is the negative class
sensitivity <- conf_matrix[2, 2] / (conf_matrix[2, 2] + conf_matrix[2, 1])
specificity <- conf_matrix[1, 1] / (conf_matrix[1, 1] + conf_matrix[1, 2])
print(paste("Sensitivity:", sensitivity))
print(paste("Specificity:", specificity))

# Make Predictions for new data (example)
new_data <- data.frame(Size = c(0.5), Weight = c(-0.2), Sweetness = c(1.0), Crunchiness = c(0.8), Juiciness = c(0.5), Ripeness = c(-0.3), Acidity = c(0.4))
predicted_quality <- predict(logistic_model, newdata = new_data, type = "response")
predicted_class_new <- ifelse(predicted_quality > 0.5, "good", "bad")
print(predicted_class_new)

