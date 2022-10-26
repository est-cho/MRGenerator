
rm(list = ls())

library(dplyr)
library(ggplot2)
library(grid)
library(rpart)

init_mr <- "init_1_"

data_path <- 'output/config_0.6_1.2_180/'
image_path <- 'output/config_0.6_1.2_180/boxplots/'


train_1 <- list.files(data_path, pattern = paste0("^", init_mr, "tr_"))
test_1 <- list.files(data_path, pattern = paste0("^", init_mr, "test_"))

df_train_1 = read.csv(paste(data_path, train_1, sep=""), skip = 6, header = TRUE)
initial_train_1 <- df_train_1 %>% slice(c(1))
df_train_1 <- df_train_1 %>% slice(-c(1, 2))

df_train_1$mr <- paste("if", trimws(df_train_1$LPLV), trimws(df_train_1$LPOP), trimws(df_train_1$LPRV),
                       ", then", trimws(df_train_1$RPLV), trimws(df_train_1$RPOP), trimws(df_train_1$RPRV))


df_test_1 = read.csv(paste(data_path, test_1, sep=""), skip = 6, header = TRUE)
initial_test_1 <- df_test_1 %>% slice(c(1))
df_test_1 <- df_test_1 %>% slice(-c(1, 2))

df_test_1$mr <- paste("if", trimws(df_test_1$LPLV), trimws(df_test_1$LPOP), trimws(df_test_1$LPRV),
                       ", then", trimws(df_test_1$RPLV), trimws(df_test_1$RPOP), trimws(df_test_1$RPRV))

join_df <- inner_join(df_train_1, df_test_1)
head(df_train_1$mr, n=15)
head(df_test_1$mr, n=15)

init_train_1 <- initial_train_1 %>% select(contains("score")) %>% select(-(Score))
init_train_1 <- mutate_all(init_train_1, function(x) as.numeric(as.character(x)))
scores_train_1 <- df_train_1 %>% select(contains("score")) %>% select(-(Score))
scores_train_1 <- mutate_all(scores_train_1, function(x) as.numeric(as.character(x)))
# names(scores_train_1)[names(scores_train_1) == 'Score'] <- 'avg_train_score'

init_test_1 <- initial_test_1 %>% select(contains("score")) %>% select(-(Score))
init_test_1 <- mutate_all(init_test_1, function(x) as.numeric(as.character(x)))
scores_test_1 <- df_test_1 %>% select(contains("score")) %>% select(-(Score))
scores_test_1 <- mutate_all(scores_test_1, function(x) as.numeric(as.character(x)))
# names(scores_test_1)[names(scores_test_1) == 'Score'] <- 'avg_test_score'


init_train_1_transpose <- data.frame(t(init_train_1))
colnames(init_train_1_transpose) <- 'init_mr'
scores_train_1_transpose <- data.frame(t(scores_train_1))
# summary(scores_train_1_transpose)
# head(scores_train_1_transpose, n=40)

init_test_1_transpose <- data.frame(t(init_test_1))
colnames(init_test_1_transpose) <- 'init_mr'
scores_test_1_transpose <- data.frame(t(scores_test_1))
# summary(scores_test_1_transpose)
# head(scores_test_1_transpose, n=40)

init_train_1_transpose$type <- 'train'
init_test_1_transpose$type <- 'test'
init_merge <- rbind(init_train_1_transpose, init_test_1_transpose)

scores_train_1_transpose$type <- 'train'
scores_test_1_transpose$type <- 'test'
scores_merge <- rbind(scores_train_1_transpose, scores_test_1_transpose)


# Plotting the data
x_width <- 600
y_height <- 600

title = paste0(init_mr, 'mr')
df <- init_merge %>% select(c("type", "init_mr"))
colnames(df) <- c('type', 'score')
png(file=paste(image_path, title,".png",sep=""),width = x_width, height = y_height)
grid.newpage()
grid.draw(ggplot(df, aes(x=type, y=score)) 
          + geom_boxplot() 
          + stat_summary(fun=mean, geom="text", show.legend = FALSE, 
                         vjust=-0.7, aes( label=round(..y.., digits=1)))
          + ggtitle(title))
dev.off()


for (i in 1:ncol(scores_merge)) {
  title = paste0(init_mr, sprintf('mr_%d', i))
  print(title)
  mr = sprintf('X%d', i)
  df <- scores_merge %>% select(c("type", all_of(mr)))
  colnames(df) <- c('type', 'score')
  png(file=paste(image_path, title,".png",sep=""),width = x_width, height = y_height)
  grid.newpage()
  grid.draw(ggplot(df, aes(x=type, y=score)) 
            + geom_boxplot() 
            + stat_summary(fun=mean, geom="text", show.legend = FALSE, 
                           vjust=-0.7, aes( label=round(..y.., digits=1)))
            + ggtitle(title))
  dev.off()
  if (i >= 100) {
    print('on last column, break')
    break
  }
}

