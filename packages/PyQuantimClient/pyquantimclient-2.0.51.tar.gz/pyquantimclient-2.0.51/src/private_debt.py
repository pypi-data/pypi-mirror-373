from .api import quantim

class private_debt_data(quantim):
    def __init__(self, username, password, secretpool, env="pdn", api_url=None):
        super().__init__(username, password, secretpool, env, api_url)

    def load_automatic_email(self, file_path):
        '''
        Load automatic email file to s3.
        '''
        # Validate filename:
        filename = file_path.split('/')[-1]
        if filename.split('.')[-1]!='xlsx':
            raise ValueError('Extension must be xlsx. Please check file.')

        resp = self.upload_with_presigned_url(file_path, "condor-credit", f"input/private_debt/automatic_email/automaticemail_privatedebt.xlsx")
        return resp
