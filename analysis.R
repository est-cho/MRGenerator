
rm(list = ls())

library(dplyr)
library(ggplot2)
library(grid)
library(rpart)

data_path <- 'output/config_0.6_1.2_180/'
image_path <- 'output/config_0.6_1.2_180/boxplots/'

train_1 <- list.files(data_path, pattern = "^init_1_tr_")
test_1 <- list.files(data_path, pattern = "^init_1_test_")

df_train_1 = read.csv(paste(data_path, train_1, sep=""), skip = 6, header = TRUE)
initial_train_1 <- df_train_1 %>% slice(c(1))
df_train_1 <- df_train_1 %>% slice(-c(1, 2))

df_test_1 = read.csv(paste(data_path, test_1, sep=""), skip = 6, header = TRUE)
initial_test_1 <- df_test_1 %>% slice(c(1))
df_test_1 <- df_test_1 %>% slice(-c(1, 2))

scores_train_1 <- df_train_1 %>% select(contains("score")) %>% select(-(Score))
scores_train_1 <- mutate_all(scores_train_1, function(x) as.numeric(as.character(x)))
names(scores_train_1)[names(scores_train_1) == 'Score'] <- 'avg_train_score'
# scores_train_1$type = 'train'
head(scores_train_1)


scores_test_1 <- df_test_1 %>% select(contains("score")) %>% select(-(Score))
scores_test_1 <- mutate_all(scores_test_1, function(x) as.numeric(as.character(x)))
names(scores_test_1)[names(scores_test_1) == 'Score'] <- 'avg_test_score'
# scores_test_1$type = 'test'
str(scores_test_1)

scores_train_1_transpose <- data.frame(t(scores_train_1))
summary(scores_train_1_transpose)
# scores_transpose %>% select(X40:X45)
# boxplot(scores_train_1_transpose)
head(scores_train_1_transpose, n=40)

scores_test_1_transpose <- data.frame(t(scores_test_1))
summary(scores_test_1_transpose)
# scores_transpose %>% select(X40:X45)
# boxplot(scores_test_1_transpose)
head(scores_test_1_transpose, n=40)

# i = 1
# title = cat(sprintf('MR %d', i))
# mr_num = cat(sprintf('X%d', i))
# mr_train <- scores_train_1_transpose %>% select(c(1))
# mr_train$type <- 'train'
# mr_train <- mr_train %>% rename(file = 0)
# colnmaes(mr_train) <- c("Files", "X1")
# mr_test <- scores_test_1_transpose %>% select(c(1))
# mr_test$type <- 'test'
# str(mr_train)
# str(mr_test)
# mr_merge <- rbind(mr_train, mr_test)
# str(mr_merge)
# ggplot(mr_merge, aes(x=type, y=mr_merge)) + geom_boxplot()

scores_train_1_transpose$type <- 'train'
scores_test_1_transpose$type <- 'test'
scores_merge <- rbind(scores_train_1_transpose, scores_test_1_transpose)
head(scores_merge)

# scores_merge[1]
# colnames(scores_merge)
# 
# for (col in colnames(scores_merge)) {
#   ggplot(scores_merge, aes(x=type, y=X56)) + geom_boxplot()
#   
#   config_time <- substring(file,5,nchar(file)-4)
#   filename <- paste0("timeseries_",config_time)
#   png(file=paste(image_path, filename,".png",sep=""),width = x_width, height = y_width)
#   
#   grid.newpage()
#   grid.draw(rbind(ggplotGrob(color),ggplotGrob(distance),ggplotGrob(angle),ggplotGrob(speed)))
#   dev.off()
# }



x_width <- 200
y_height <- 200

for (i in 1:ncol(scores_merge)) {
  title = sprintf('MR %d', i)
  print(title)
  mr = sprintf('X%d', i)
  df <- scores_merge %>% select(c("type", all_of(mr)))
  colnames(df) <- c('type', 'score')
  png(file=paste(image_path, title,".png",sep=""),width = x_width, height = y_height)
  grid.newpage()
  grid.draw(ggplot(df, aes(x=type, y=score)) + geom_boxplot())
  dev.off()
  if (i >= 100) {
    print('on last column, break')
    break
  }
}
