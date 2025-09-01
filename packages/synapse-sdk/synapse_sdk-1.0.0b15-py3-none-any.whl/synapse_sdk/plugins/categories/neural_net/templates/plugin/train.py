import time


def train(run, dataset, hyperparameter, checkpoint=None):
    count_epochs = hyperparameter['epochs']
    run.set_progress(0, count_epochs, category='train')
    for i in range(1, count_epochs + 1):
        time.sleep(0.5)
        loss = float(round((count_epochs - i) / count_epochs, 2))
        miou = 1 - loss
        run.log_metric('epoch', i, loss=loss, miou=miou)
        run.set_progress(i, count_epochs, category='train')
    return './'
